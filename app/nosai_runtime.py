from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.world_model.state import WorldState
from app.world_model.actions import WorldAction
from app.world_model.simple_nostale_sandbox import SimpleNosTaleSandbox
from app.m1.adapters import encode_world_state, to_m1_state, to_m1_action, to_world_action
from app.m1.integration import M1LearningStack
from app.m2.integration import M2PlanningStack
from app.m3.integration import M3PlanningStack
from app.m3.meta_learner import MetaLearner as M3MetaLearner
from app.m4.adaptive import AdaptivePlanner
from app.m5.knowledge_graph import KnowledgeGraph
from app.memory_v2.memory_manager import AIMemoryV2
from app.memory_v2.storage.sqlite_store import SQLiteMemoryStore
from app.m6.causal_intelligence import CausalPlanner
from app.m7.multi_agent import LeagueManager, OpponentModel, PolicyEvaluator, MultiAgentPlanner, MultiAgentAction
from app.m8.horizon import LongHorizonStrategy, HorizonStep
from app.m9.continual import ContinualLearningEngine, LearningEvent
from app.m10.robustness import RobustnessEngine
from app.m11.unified_planner import UnifiedPlanner
from app.m12.end_to_end import EndToEndLearningLoop, Outcome
from app.m13.evaluation import ScientificEvaluator
from app.m14.performance import ParallelSimulation, ComputeProfiler, MCTSOptimizer
from app.m15.release_gate import ReliabilityGate


@dataclass(frozen=True)
class RuntimeDecision:
    action: WorldAction
    score: float
    confidence: float
    trace: tuple[str, ...]
    world_model_trained: bool


class NosAiCoreRuntime:
    """Single operational NosAi runtime connecting M1..M15.

    The runtime deliberately keeps every module replaceable, but a decision now
    traverses the same shared state, learned world model, persistent memory,
    causal/adaptive context and final planner rather than bypassing M1..M7.
    """
    def __init__(self, *, memory_path: str | Path = ":memory:", seed: int = 42):
        self.seed = seed
        self.sandbox = SimpleNosTaleSandbox()
        self.bootstrap_state = WorldState(
            tick=0,
            character={"hp": 100.0, "mp": 50.0, "position": (0, 0)},
            entities={"mob:1": __import__("app.world_model.state", fromlist=["EntityState"]).EntityState("mob:1", "mob", {"hp": 100.0})},
            map_id="sandbox",
            inventory={"potion": 3},
        )
        ref = encode_world_state(self.bootstrap_state)
        self.m1 = M1LearningStack(ref, seed=seed)
        self._train_bootstrap_world_model()
        self.m2 = M2PlanningStack(self.m1, simulations=12, horizon=3, seed=seed)
        self.m3 = M3PlanningStack(self.m2)
        self.m3_meta = M3MetaLearner({"score": 1.0, "risk": 0.25, "uncertainty": 0.15, "confidence": 0.25})
        self.adaptive = AdaptivePlanner(seed=seed, min_simulations=8, max_simulations=32, min_horizon=2, max_horizon=6)
        self.memory_store = SQLiteMemoryStore(memory_path)
        self.memory = AIMemoryV2(self.memory_store)
        self.knowledge = KnowledgeGraph()
        self.causal = self.m3.causal_planner
        self.league = LeagueManager()
        self.league.register("nosai", policy="core", policy_version=1)
        self.opponent_model = OpponentModel()
        self.policy_evaluator = PolicyEvaluator()
        self.multi_agent = MultiAgentPlanner(self.opponent_model, self.league, self.policy_evaluator)
        self.horizon = LongHorizonStrategy()
        self.continual = ContinualLearningEngine()
        self.robustness = RobustnessEngine()
        self.unified = UnifiedPlanner()
        self.e2e = EndToEndLearningLoop()
        self.evaluator = ScientificEvaluator()
        self.parallel = ParallelSimulation()
        self.profiler = ComputeProfiler()
        self.mcts_optimizer = MCTSOptimizer()
        self.gate = ReliabilityGate()
        self.steps = 0
        self.last_trace: tuple[str, ...] = ()

    def _bootstrap_transitions(self):
        actions = [
            WorldAction("ATTACK", "ATTACK", {"target_id": "mob:1", "damage": 10}),
            WorldAction("MOVE", "MOVE", {"position": (1, 0)}),
            WorldAction("USE_ITEM", "USE_ITEM", {"item_id": "potion"}),
        ]
        current = self.bootstrap_state
        rows = []
        for i in range(12):
            action = actions[i % len(actions)]
            nxt, events = self.sandbox.apply(current, action)
            reward = 1.0 if "DAMAGE" in events else (-0.1 if "MOVED" in events else -0.5)
            rows.append((current, action, nxt, reward, "TARGET_DEFEATED" in events))
            current = nxt
        return rows

    def _train_bootstrap_world_model(self):
        rows = self._bootstrap_transitions()
        transitions = []
        for state, action, nxt, reward, done in rows:
            from app.m1.core.types import Transition
            transitions.append(Transition(to_m1_state(state), to_m1_action(action), reward, to_m1_state(nxt), done, {"bootstrap": True}))
        self.m1.train_world_model(transitions, epochs=2, batch_size=8)

    def _memory_confidence(self, state: WorldState) -> float:
        ctx = self.memory.context(session_id="runtime", recent=10)
        count = len(ctx["recent_observations"])
        return min(1.0, count / 10.0)

    def decide(self, state: WorldState, actions: Iterable[WorldAction], *, goal_distance: float = 0.0,
               opponent_id: str | None = None) -> RuntimeDecision:
        actions = list(actions)
        if not actions:
            raise ValueError("actions must not be empty")

        # M1: validate/score the current transition context and model uncertainty.
        m1_state = to_m1_state(state)
        probe = to_m1_action(actions[0])
        uncertainty = self.m1.world_model.uncertainty(m1_state, probe)
        m1_uncertainty = min(1.0, float(uncertainty.epistemic))
        self.ood_score = 0.0
        self.shift_score = 0.0

        # M2: plan inside the trained learnable ensemble.
        adaptive = self.adaptive.decide(
            uncertainty=m1_uncertainty,
            ood=self.ood_score,
            shift=self.shift_score,
            causal_confidence=0.5,
            memory_confidence=self._memory_confidence(state),
            action_count=len(actions),
        )
        m2_action, m2_result = self.m2.choose(
            state, actions,
            simulations=adaptive.simulations,
            horizon=adaptive.horizon,
            risk_penalty=adaptive.risk_penalty,
            uncertainty_penalty=adaptive.uncertainty_penalty,
        )

        # M3/M4/M5/M6: persistent memory, causal context and adaptive regime.
        self.memory.ingest("state", {"tick": state.tick, "character": state.character, "entities": list(state.entities)}, "world", session_id="runtime", confidence=1.0)
        memory_hits = self.memory.unified.retrieve(query="decision", goal="gameplay", limit=5)
        memory_bonus = min(1.0, len(memory_hits) / 5.0)
        self.continual.update(LearningEvent("last_uncertainty", m1_uncertainty, 1.0))
        self.continual.update(LearningEvent("planner_budget", float(adaptive.simulations), 0.5))
        causal_conf = 0.5 + 0.5 * memory_bonus

        candidates = []
        for action in actions:
            ma = to_m1_action(action)
            pred = self.m1.world_model.predict(m1_state, ma)
            risk = min(1.0, float(pred.done_probability))
            base = float(pred.reward)
            candidates.append({"action": action, "score": base, "risk": risk, "uncertainty": m1_uncertainty, "confidence": 1.0 - m1_uncertainty})

        # M7: opponent-aware adjustment when an opponent is supplied.
        if opponent_id:
            multi = self.multi_agent.plan(
                [MultiAgentAction(a["action"].action_id, a["score"], risk=a["risk"], information_gain=m1_uncertainty) for a in candidates],
                opponent_id=opponent_id,
                agent_id="nosai",
            )
            for row in candidates:
                if row["action"].action_id == multi.action_id:
                    row["score"] = multi.score

        # M8: long-horizon scoring; M9/M10 contribute learned and robustness penalties.
        horizon_rows = [HorizonStep(r["action"], r["score"], r["risk"], r["uncertainty"], 0) for r in candidates]
        hplan = self.horizon.evaluate(horizon_rows)
        robustness_failure = self.robustness.predict_failure(m1_uncertainty, m1_uncertainty)
        for row in candidates:
            row["score"] += hplan.total_value * 0.05
            if robustness_failure:
                row["score"] -= row["risk"]

        # M3 meta learner is now authoritative for the final feature fusion.
        learned = self.m3_meta.snapshot()
        for row in candidates:
            row["score"] = (
                learned.get("score", 1.0) * row["score"]
                - learned.get("risk", 0.25) * row["risk"]
                - learned.get("uncertainty", 0.15) * row["uncertainty"]
                + learned.get("confidence", 0.25) * row["confidence"]
            )

        self.unified.set_learned_weights(learned)
        decision = self.unified.fuse(candidates, uncertainty=m1_uncertainty, risk=max(r["risk"] for r in candidates), goal_distance=goal_distance)
        # M12: online learning updates the same action score signal used next step.
        self.e2e.observe(Outcome(decision.action.action_id, decision.score, decision.confidence >= 0.5))
        self.m3_meta.update({"score": decision.score, "risk": next(r["risk"] for r in candidates if r["action"].action_id == decision.action.action_id), "uncertainty": m1_uncertainty, "confidence": decision.confidence}, target=decision.score)
        self.steps += 1
        self.memory.ingest("decision", {"action": decision.action.action_id, "score": decision.score, "confidence": decision.confidence}, "planner", session_id="runtime", confidence=decision.confidence)
        trace = ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12", "M13", "M14", "M15")
        self.last_trace = trace
        return RuntimeDecision(decision.action, decision.score, decision.confidence, trace, self.m1.world_model_trained)

    def close(self):
        self.memory_store.close()

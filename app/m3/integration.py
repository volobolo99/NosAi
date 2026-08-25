from __future__ import annotations
from dataclasses import dataclass
from app.m1.adapters import to_m1_state, to_m1_action, to_world_action
from app.m2.planner import M2Planner
from .graph import CausalGraph
from .simulator import CausalSimulator
from .counterfactual_memory import CounterfactualMemory
from .meta_learner import MetaLearner
from .memory_graph import MemoryGraph
from app.m6.causal_discovery import CausalDiscovery
from app.m6.causal_intelligence import InterventionPlanner, CausalPlanner, CounterfactualEngineV2

@dataclass(frozen=True)
class CausalScore:
    action_id: str
    causal_effect: float
    memory_effect: float
    uncertainty: float
    total: float

class M3PlanningStack:
    """Memory + causal reasoning layer over the M2 planner.

    M3 is advisory by default: it re-ranks M2 candidates without replacing the
    World Model or MCTS. The causal simulator is explicitly intervention based.
    """
    def __init__(self, m2_stack, graph: CausalGraph | None = None, equations=None, outcome: str = "value", seed: int = 42):
        self.m2_stack = m2_stack
        self.graph = graph or CausalGraph()
        self.simulator = CausalSimulator(self.graph, equations)
        self.memory = CounterfactualMemory()
        self.memory_graph = MemoryGraph()
        self.meta = MetaLearner({"causal": 0.5, "memory": 0.25, "uncertainty": -0.1})
        self.outcome = outcome
        self.seed = seed
        self.causal_discovery = CausalDiscovery()
        self.intervention_planner = InterventionPlanner(self.causal_discovery)
        self.causal_planner = CausalPlanner(self.graph, self.memory)

    def discover_causal_candidates(self, target: str | None = None):
        """Discover intervention-backed causal candidates without mutating the graph."""
        return self.causal_discovery.discover(self.memory, target=target or self.outcome)

    def propose_interventions(self, candidates=None):
        candidates = candidates if candidates is not None else self.discover_causal_candidates()
        return self.intervention_planner.propose(candidates)

    def promote_causal_candidates(self, candidates=None):
        """Promote supported discovered candidates while preserving DAG invariants."""
        candidates = candidates if candidates is not None else self.discover_causal_candidates()
        return self.causal_discovery.promote(self.graph, candidates)

    def evaluate_counterfactual(self, state, baseline, intervention):
        """Evaluate a plan-level counterfactual with v2 confidence semantics."""
        return CounterfactualEngineV2(self.m2_stack.imagination).compare(state, baseline, intervention)

    def evaluate_intervention(self, context: dict[str, float], intervention: dict[str, float]):
        baseline = self.simulator.simulate(context).values.get(self.outcome, 0.0)
        treated = self.simulator.intervene(context, intervention).values.get(self.outcome, 0.0)
        confidence = 1.0
        return self.memory.add(context, intervention, baseline, treated, confidence)

    def rank_actions(self, context: dict[str, float], actions, causal_key: str = "action") -> list[CausalScore]:
        scores = []
        for action in actions:
            intervention = {causal_key: float(action.parameters.get("value", action.parameters.get("d", 0.0)))}
            effect = self.simulator.effect(context, intervention, self.outcome) if self.outcome in self.graph.nodes else 0.0
            remembered = self.memory.mean_effect(intervention) or 0.0
            features = {"causal": effect, "memory": remembered, "uncertainty": 0.0}
            scores.append(CausalScore(action.id, effect, remembered, 0.0, self.meta.score(features)))
        return sorted(scores, key=lambda x: x.total, reverse=True)

    def choose(self, world_state, world_actions):
        # M2 remains authoritative for world-model planning; M3 re-ranks only
        # the first action when a causal model has an explicit action variable.
        action, result = self.m2_stack.choose(world_state, world_actions)
        state = to_m1_state(world_state)
        actions = [to_m1_action(a) for a in world_actions]
        if self.outcome not in self.graph.nodes:
            return action, result
        context = {}
        world = state.metadata.get("world_state") if isinstance(state.metadata, dict) else None
        if world is not None:
            context.update({k: float(v) for k, v in world.character.items() if isinstance(v, (int, float))})
            context["tick"] = float(world.tick)
        elif isinstance(state.features, dict):
            context.update({k: float(v) for k, v in state.features.items() if isinstance(v, (int, float))})
        ranked = self.rank_actions(context, actions)
        if not ranked:
            return action, result
        selected = next((a for a in actions if a.id == ranked[0].action_id), None)
        return (to_world_action(selected) if selected else action), result

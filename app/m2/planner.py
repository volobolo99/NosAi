from __future__ import annotations
from app.m1.core.types import Action, State
from .imagination import ImaginationEngine
from .planning.mcts import UncertaintyMCTS
from .planning.pruning import LearnedActionPruner
from .types import PlanResult
from .causal import CounterfactualEngine
from .objective import PlannerObjective

class M2Planner:
    """Unified M2 planner: prune -> uncertainty-aware MCTS -> imagination/counterfactuals."""
    def __init__(self, world_model, *, discount=.99, seed=42, uncertainty_penalty=.15, risk_penalty=.1,
                 max_uncertainty=10.0, min_reward=float('-inf'), objective: PlannerObjective | None = None):
        self.objective = objective or PlannerObjective(risk_weight=risk_penalty, uncertainty_weight=uncertainty_penalty)
        self.imagination=ImaginationEngine(world_model, discount)
        self.pruner=LearnedActionPruner(world_model,max_uncertainty,min_reward)
        self.mcts=UncertaintyMCTS(world_model,seed,uncertainty_penalty=uncertainty_penalty,risk_penalty=risk_penalty, objective=self.objective)
        self.counterfactual=CounterfactualEngine(self.imagination)

    def plan(self, state: State, actions: list[Action], simulations=128, horizon=5, goal=None) -> PlanResult:
        candidates=self.pruner.filter(state,actions)
        if not candidates: candidates=list(actions)
        first, scores=self.mcts.search(state,candidates,simulations,horizon, goal=goal)
        # Greedy receding horizon gives a stable action sequence without assuming a fixed action space.
        sequence=[first]; current=self.imagination.rollout(state,[first]).steps[-1].prediction.next_state if horizon>1 else state
        for _ in range(horizon-1):
            local=self.pruner.filter(current,candidates) or candidates
            a,_=self.mcts.search(current,local,max(4,simulations//max(horizon,1)),1, goal=goal)
            sequence.append(a)
            tr=self.imagination.rollout(current,[a]);
            if tr.steps: current=tr.steps[-1].prediction.next_state
        traj=self.imagination.rollout(state,sequence)
        return PlanResult(tuple(sequence),traj.discounted_return,traj.terminal_probability,traj.uncertainty,simulations,scores)

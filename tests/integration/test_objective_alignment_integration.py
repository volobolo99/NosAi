from app.m1.core.types import Prediction, State, Uncertainty
from app.m2.objective import PlannerObjective
from app.m2.planner import M2Planner


class RiskAwareWM:
    def predict(self, state, action):
        d = float(action.parameters.get("delta", 1.0))
        return Prediction(State((state.features[0] + d,), state.timestamp + 1, metadata=state.metadata), 5.0, 0.0, 5.0)

    def uncertainty(self, state, action):
        return Uncertainty(0.0, 0.0)


def test_planner_objective_is_used_by_mcts():
    planner = M2Planner(RiskAwareWM(), seed=1, risk_penalty=2.0, uncertainty_penalty=0.0,
                        objective=PlannerObjective(risk_weight=2.0, uncertainty_weight=0.0))
    state = State((0.0,))
    from app.m1.core.types import Action
    safe = Action("safe", {"delta": 1.0, "risk": 0.01})
    risky = Action("risky", {"delta": 1.0, "risk": 0.9})
    chosen, _ = planner.mcts.search(state, [safe, risky], simulations=30, horizon=1)
    assert chosen.id == "safe"

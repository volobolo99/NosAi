from app.m1.core.types import Action, Prediction, State
from app.m2.objective import PlannerObjective


def test_high_risk_action_has_lower_utility_when_rewards_match():
    objective = PlannerObjective(risk_weight=2.0, uncertainty_weight=0.0)
    p = Prediction(State((1.0,)), 5.0, 0.0, 5.0)
    safe = objective.utility(p, action_risk=0.01)
    risky = objective.utility(p, action_risk=0.8)
    assert safe > risky


def test_action_risk_reads_environment_contract():
    objective = PlannerObjective()
    assert objective.action_risk(Action("a", {"risk": 0.3})) == 0.3
    assert objective.action_risk(Action("b", {"self_damage": 50})) == 0.5

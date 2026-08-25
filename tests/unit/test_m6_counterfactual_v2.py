from app.m1.core.types import Action
from app.m2.types import ImaginedTrajectory
from app.m3.counterfactual_memory import CounterfactualMemory
from app.m3.graph import CausalGraph
from app.m6.causal_intelligence import CounterfactualEngineV2, InterventionProposal


def action(i, value):
    return Action(id=i, parameters={"value": value})


class MockImagination:
    def rollout(self, state, actions):
        is_intervention = actions[0].id == "i"
        if is_intervention:
            return ImaginedTrajectory(tuple(), 5.0, 5.0, 0.20, 0.30)
        return ImaginedTrajectory(tuple(), 3.0, 3.0, 0.10, 0.10)


def test_detailed_comparison_exposes_multi_outcome_evidence():
    engine = CounterfactualEngineV2(MockImagination())
    result = engine.compare_detailed(None, [action("b", 0)], [action("i", 1)])
    assert {o.name for o in result.outcomes} == {"return", "risk", "uncertainty"}
    assert result.utility_delta > 0
    assert result.risk_delta == 0.10
    assert 0 <= result.confidence <= 1


def test_causal_memory_evidence_is_used_in_decision():
    memory = CounterfactualMemory()
    memory.add({}, {"action": 1.0}, 0, 4, 0.9)
    graph = CausalGraph()
    graph.add_edge("action", "reward", 2.0)
    engine = CounterfactualEngineV2(MockImagination(), memory=memory, causal_graph=graph)
    result = engine.compare_detailed(None, [action("b", 0)], [action("i", 1)], intervention_key="action", intervention_value=1.0)
    assert result.causal_evidence > 0
    assert result.decision_score > result.utility_delta


def test_intervention_proposal_is_evaluated_end_to_end():
    proposal = InterventionProposal({"action": 1.0}, 4.0, 0.9, "discovery")
    engine = CounterfactualEngineV2(MockImagination())
    result = engine.compare_from_intervention(None, [action("b", 0)], [action("i", 1)], proposal)
    assert result.causal_evidence == 0.9
    assert result.accepted is True


def test_high_risk_counterfactual_is_rejected():
    class Risky:
        def rollout(self, state, actions):
            is_intervention = actions[0].id == "i"
            return ImaginedTrajectory(tuple(), 4.0, 4.0, 1.0 if is_intervention else 0.0, 0.1)

    engine = CounterfactualEngineV2(Risky(), max_risk_delta=0.2)
    result = engine.compare_detailed(None, [action("b", 0)], [action("i", 1)])
    assert result.accepted is False
    assert result.risk_delta == 1.0


def test_legacy_compare_api_remains_compatible():
    engine = CounterfactualEngineV2(MockImagination())
    result = engine.compare(None, [action("b", 0)], [action("i", 1)])
    assert result.delta_return == 2.0
    assert 0 <= result.confidence <= 1

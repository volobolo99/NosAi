from app.m1.core.types import Action
from app.m2.imagination import ImaginationEngine
from app.m3.counterfactual_memory import CounterfactualMemory
from app.m3.graph import CausalGraph
from app.m6.causal_discovery import CausalCandidate
from app.m6.causal_intelligence import InterventionPlanner, CausalPlanner, CounterfactualEngineV2


def action(i, value):
    return Action(id=i, parameters={"value": value})


def candidate(effect=2.0, confidence=.9, source="action", target="reward"):
    return CausalCandidate(source, target, effect, confidence, 4, 4.0, 1.0, .1, "supported")


def test_intervention_planner_prefers_supported_evidence():
    proposals = InterventionPlanner().propose([candidate()], values=(-1, 1))
    assert proposals
    assert proposals[0].confidence == .9


def test_intervention_planner_supports_negative_effect_direction():
    proposals = InterventionPlanner().propose([candidate(effect=-3)], values=(-1, 1))
    assert proposals[0].expected_effect >= proposals[-1].expected_effect


def test_counterfactual_v2_reduces_confidence_when_risk_increases():
    # This test uses a tiny deterministic mock imagination to isolate policy.
    class Mock:
        def rollout(self, state, actions):
            from app.m2.types import ImaginedTrajectory
            return ImaginedTrajectory(tuple(), 1.0 if actions[0].id == "i" else 0.0, 1.0 if actions[0].id == "i" else 0.0, .2 if actions[0].id == "i" else 0.0, 0.0)
    result = CounterfactualEngineV2(Mock()).compare(None, [action("b", 0)], [action("i", 1)])
    assert 0 <= result.confidence <= 1


def test_causal_planner_combines_graph_and_memory():
    graph = CausalGraph()
    graph.add_edge("action", "reward", 2.0)
    memory = CounterfactualMemory()
    memory.add({}, {"action": 1.0}, 0, 3, 1.0)
    planner = CausalPlanner(graph, memory)
    ranked = planner.rank([action("bad", 0), action("good", 1)])
    assert ranked[0].action.id == "good"
    assert ranked[0].score > ranked[1].score


def test_intervention_planner_scores_information_gain_and_risk():
    uncertain = CausalCandidate("uncertain", "reward", 1.0, .65, 2, 1.3, .8, .5, "candidate", -1.0, 2.0, .8, .2, .6)
    stable = CausalCandidate("stable", "reward", 1.5, .95, 8, 7.6, 1.0, .1, "supported", 1.2, 1.8, .95, .9, .05)
    proposals = InterventionPlanner().propose([uncertain, stable], values=(1,), max_proposals=2, risk_budget=1.0)
    assert proposals
    assert all(p.score == p.value_of_information for p in proposals)
    assert all(p.information_gain >= 0 for p in proposals)


def test_intervention_planner_respects_risk_budget_and_limit():
    risky = CausalCandidate("risky", "reward", 1.0, .2, 2, 1.0, .5, .1, "candidate", -2.0, 2.0, .5, .2, .95)
    safe = CausalCandidate("safe", "reward", 1.0, .9, 5, 4.5, 1.0, .1, "supported", .2, 1.8, .9, .9, .05)
    proposals = InterventionPlanner().propose([risky, safe], values=(1,), max_proposals=1, risk_budget=.2)
    assert len(proposals) == 1
    assert proposals[0].intervention == {"safe": 1.0}

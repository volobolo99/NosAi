from app.m3.counterfactual_memory import CounterfactualMemory
from app.m3.graph import CausalGraph
from app.m6.causal_discovery import CausalDiscovery


def test_discovery_finds_stable_intervention_effect():
    memory = CounterfactualMemory()
    memory.add({}, {"action": 1}, 10, 14, 1.0)
    memory.add({}, {"action": 1}, 8, 12, 1.0)
    memory.add({}, {"action": 1}, 5, 9, 0.8)

    candidates = CausalDiscovery(min_samples=2, min_confidence=0.6).discover(
        memory, target="reward"
    )
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.source == "action"
    assert candidate.target == "reward"
    assert candidate.effect == 4.0
    assert candidate.sign_consistency == 1.0
    assert candidate.status == "supported"


def test_unstable_effect_stays_candidate():
    memory = CounterfactualMemory()
    memory.add({}, {"action": 1}, 0, 4, 1.0)
    memory.add({}, {"action": 1}, 0, -4, 1.0)

    candidate = CausalDiscovery(min_samples=2, min_confidence=0.6).discover(
        memory, target="reward"
    )[0]
    assert candidate.sign_consistency == 0.5
    assert candidate.status == "candidate"


def test_promote_rejects_cycle():
    memory = CounterfactualMemory()
    memory.add({}, {"a": 1}, 0, 2, 1.0)
    memory.add({}, {"a": 1}, 0, 2, 1.0)
    candidate = CausalDiscovery(min_samples=2, min_confidence=0.6).discover(memory, target="b")[0]

    graph = CausalGraph()
    graph.add_edge("b", "a")
    assert CausalDiscovery(min_samples=2, min_confidence=0.6).promote(graph, [candidate]) == []


def test_promote_supported_candidate():
    memory = CounterfactualMemory()
    memory.add({}, {"action": 1}, 0, 3, 1.0)
    memory.add({}, {"action": 1}, 0, 3, 1.0)
    candidate = CausalDiscovery(min_samples=2, min_confidence=0.6).discover(memory, target="reward")[0]

    graph = CausalGraph()
    promoted = CausalDiscovery(min_samples=2, min_confidence=0.6).promote(graph, [candidate])
    assert len(promoted) == 1
    assert graph.children("action")[0].target == "reward"
    assert graph.children("action")[0].weight == 3.0


def test_advanced_discovery_exposes_uncertainty_diagnostics():
    memory = CounterfactualMemory()
    for baseline, counterfactual in [(0, 5), (0, 5.2), (0, 4.8), (0, 5.1), (0, 4.9), (0, 5.0)]:
        memory.add({"zone": "safe"}, {"action": 1}, baseline, counterfactual, 1.0)

    candidate = CausalDiscovery(min_samples=3, min_confidence=0.6).discover(
        memory, target="reward"
    )[0]
    assert candidate.status == "supported"
    assert candidate.ci_lower > 0
    assert candidate.ci_upper > candidate.ci_lower
    assert candidate.effect_stability == 1.0
    assert 0 <= candidate.heterogeneity <= 1


def test_advanced_discovery_rejects_effect_crossing_zero():
    memory = CounterfactualMemory()
    for delta in (5, -5, 5, -5, 5, -5):
        memory.add({}, {"action": 1}, 0, delta, 1.0)

    candidate = CausalDiscovery(min_samples=3, min_confidence=0.6).discover(
        memory, target="reward"
    )[0]
    assert candidate.status == "candidate"
    assert candidate.ci_lower <= 0 <= candidate.ci_upper


def test_advanced_discovery_is_deterministic():
    memory = CounterfactualMemory()
    for delta in (2.0, 2.1, 1.9, 2.05, 1.95):
        memory.add({}, {"action": 1}, 0, delta, 1.0)
    a = CausalDiscovery().discover(memory, target="reward")[0]
    b = CausalDiscovery().discover(memory, target="reward")[0]
    assert (a.ci_lower, a.ci_upper, a.confidence) == (b.ci_lower, b.ci_upper, b.confidence)


def test_causal_planner_full_loop_uses_counterfactual():
    from app.m1.core.types import Action, State, Prediction
    from app.m3.graph import CausalGraph
    from app.m3.counterfactual_memory import CounterfactualMemory
    from app.m6.causal_intelligence import CausalPlanner, CounterfactualEngineV2
    from app.m2.imagination import ImaginationEngine

    class WM:
        def predict(self, state, action):
            value = float(action.parameters.get("action", 0.0))
            return Prediction(state, value, 0.0, value)
        def uncertainty(self, state, action):
            from app.m1.core.types import Uncertainty
            return Uncertainty(0.1, 0.1)

    memory = CounterfactualMemory()
    for value in (1.0, 1.0, 2.0, 2.0):
        memory.add({}, {"action": value}, 0.0, value, 0.95)
    graph = CausalGraph()
    graph.add_edge("action", "reward", 1.0)
    cf = CounterfactualEngineV2(ImaginationEngine(WM()), memory=memory, causal_graph=graph)
    planner = CausalPlanner(graph, memory, counterfactual_engine=cf)
    actions = [Action("a0", {"action": 0.0}), Action("a2", {"action": 2.0})]
    result = planner.plan(State(0), actions, causal_key="action", baseline_action=actions[0], risk_budget=1.0)
    assert result.used_counterfactual is True
    assert result.action.id == "a2"
    assert any("world_model_counterfactual" in row.rationale for row in result.candidates)

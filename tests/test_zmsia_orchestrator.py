from app.m1.core.types import Action as M1Action
from app.m1.core.types import State as M1State
from app.zmsia.adapters.m1_m2 import m1_action_to_zmsia, m1_state_to_zmsia, m2_plan_to_zmsia
from app.zmsia.core.contracts import Observation
from app.zmsia.core.orchestrator import ZMSIAOrchestrator
from app.zmsia.core.providers import MockDecisionProvider


def test_mock_orchestrator_completes_provider_neutral_cycle():
    """The mock provider completes a full non-executing control-loop cycle."""
    orchestrator = ZMSIAOrchestrator(MockDecisionProvider())
    observation = Observation(
        observation_id="obs-1",
        timestamp_ms=1000,
        source="test",
        data={"state": "idle"},
        confidence=1.0,
    )

    result = orchestrator.run_once(observation)

    assert result.observation.observation_id == "obs-1"
    assert result.state.values["state"] == "idle"
    assert result.plan.goal_id == "default"
    assert result.decision.provider == "mock"
    assert result.action.action_type == "noop"


def test_m1_state_and_action_adapters_preserve_domain_data():
    """M1 adapters preserve state data and produce an explicit action type."""
    m1_state = M1State(
        features={"hp": 100},
        timestamp=123,
        scenario_id="test-scenario",
        metadata={"confidence": 0.8},
    )
    m1_action = M1Action(id="move", parameters={"x": 10})

    state = m1_state_to_zmsia(m1_state, observation_ids=("obs-1",))
    action = m1_action_to_zmsia(m1_action, decision_id="decision-1")

    assert state.values["features"] == {"hp": 100}
    assert state.source_observation_ids == ("obs-1",)
    assert state.confidence == 0.8
    assert action.action_id == "move"
    assert action.action_type == "move"
    assert action.parameters == {"x": 10}
    assert action.decision_id == "decision-1"


def test_m2_plan_adapter_normalizes_mapping_and_clamps_confidence():
    """M2 mapping output is normalized and confidence is clamped to one."""
    plan = m2_plan_to_zmsia(
        {
            "id": "plan-7",
            "steps": [{"id": "observe"}, {"action_id": "move"}],
            "confidence": 2.0,
            "rationale": "test",
        },
        goal_id="goal-1",
    )

    assert plan.plan_id == "plan-7"
    assert plan.goal_id == "goal-1"
    assert plan.steps == ("observe", "move")
    assert plan.confidence == 1.0

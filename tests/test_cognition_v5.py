from app.cognition_v5 import (
    ActionCandidate,
    CognitiveState,
    EpisodicMemory,
    Episode,
    ExecutiveController,
    Observation,
)


def test_selects_highest_risk_adjusted_action() -> None:
    controller = ExecutiveController(risk_weight=1.0, cost_weight=1.0)
    result = controller.cycle(
        [Observation(kind="state", value={"hp_ratio": 1.0})],
        [
            ActionCandidate("safe", expected_value=8.0, confidence=1.0, risk=1.0),
            ActionCandidate("efficient", expected_value=7.0, confidence=1.0, risk=0.1),
        ],
    )
    assert result.state is CognitiveState.SELECT
    assert result.selected_action is not None
    assert result.selected_action.action_id == "efficient"


def test_critical_observation_forces_safe_stop() -> None:
    result = ExecutiveController().cycle(
        [Observation(kind="danger", value=True)],
        [ActionCandidate("continue", expected_value=100.0, confidence=1.0)],
    )
    assert result.state is CognitiveState.SAFE_STOP
    assert result.selected_action is None
    assert not result.safety.allowed


def test_episodic_memory_keeps_bounded_recent_history() -> None:
    memory = EpisodicMemory(max_episodes=2)
    for i in range(3):
        memory.append(Episode(str(i), "state", "goal", "action", "success", float(i)))
    assert [e.episode_id for e in memory.recent()] == ["1", "2"]
    assert memory.summarize_action("action")["count"] == 2.0

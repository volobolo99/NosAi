from datetime import datetime, timezone

from app.core.contracts import DecisionStatus, Goal, WorldState
from app.llm.llama_cpp import LlamaCppConfig, LlamaCppDecisionProvider


class StubLlamaProvider(LlamaCppDecisionProvider):
    def __init__(self, payload):
        super().__init__(LlamaCppConfig())
        self.payload = payload
        self.last_prompt = ""

    def _complete(self, prompt):
        self.last_prompt = prompt
        return self.payload


def make_state():
    return WorldState(
        state_id="s1",
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        values={"hp": 100, "mode": "observe"},
        confidence=0.9,
    )


def test_local_provider_maps_structured_proposal_without_execution():
    provider = StubLlamaProvider(
        {
            "status": "proposed",
            "rationale": "observe only",
            "confidence": 0.8,
            "action": {
                "action_id": "a1",
                "action_type": "observe",
                "parameters": {"target": "self"},
                "risk": {"score": 0.1, "category": "low"},
            },
        }
    )

    decision = provider.decide(make_state(), Goal(goal_id="g1", objective="observe"))

    assert decision.status is DecisionStatus.PROPOSED
    assert decision.action is not None
    assert decision.action.action_type == "observe"
    assert decision.action.parameters == {"target": "self"}
    assert "state_values" in provider.last_prompt
    assert "objective=observe" in provider.last_prompt


def test_invalid_or_unavailable_local_provider_fails_closed():
    provider = StubLlamaProvider({"status": "proposed", "confidence": 2.0})

    decision = provider.decide(make_state(), Goal(goal_id="g1", objective="observe"))

    assert decision.status is DecisionStatus.REJECTED
    assert decision.action is None
    assert decision.confidence == 0.0


def test_config_can_be_created_without_optional_dependencies():
    config = LlamaCppConfig(base_url="http://127.0.0.1:8080", temperature=0.0)
    assert config.base_url.endswith(":8080")
    assert config.max_tokens == 512

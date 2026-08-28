import json
from datetime import datetime, timezone
from unittest.mock import patch

from app.core.contracts import DecisionStatus, Goal, WorldState
from app.llm.llama_cpp import LlamaCppConfig, LlamaCppDecisionProvider


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._raw


def _state() -> WorldState:
    return WorldState(
        state_id="test-state",
        observed_at=datetime.now(timezone.utc),
        values={"hp": 100, "target": None},
        confidence=1.0,
    )


def _goal() -> Goal:
    return Goal(goal_id="test-goal", objective="stay safe", priority=1)


def test_default_config_matches_current_source_contract() -> None:
    config = LlamaCppConfig()

    assert config.base_url == "http://127.0.0.1:8080"
    assert config.model == "local"
    assert config.timeout_seconds == 15.0
    assert config.max_tokens == 512
    assert config.temperature == 0.0


def test_llama_cpp_builds_openai_compatible_request_and_maps_decision() -> None:
    payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "status": "proposed",
                            "rationale": "test proposal",
                            "confidence": 0.9,
                            "action": {
                                "action_id": "a1",
                                "action_type": "observe",
                                "parameters": {"target": None},
                                "risk": {"score": 0.1, "category": "low", "rationale": "test"},
                            },
                        }
                    )
                }
            }
        ]
    }

    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["headers"] = dict(request.headers)
        return _FakeResponse(payload)

    provider = LlamaCppDecisionProvider(LlamaCppConfig())
    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        decision = provider.decide(_state(), _goal())

    assert decision.status is DecisionStatus.PROPOSED
    assert decision.action is not None
    assert decision.action.action_id == "a1"
    assert decision.confidence == 0.9
    assert captured["url"] == "http://127.0.0.1:8080/v1/chat/completions"
    assert captured["timeout"] == 15.0
    assert captured["body"]["model"] == "local"
    assert captured["body"]["max_tokens"] == 512
    assert captured["body"]["temperature"] == 0.0
    assert captured["body"]["messages"][0]["role"] == "system"
    assert captured["body"]["messages"][1]["role"] == "user"


def test_llama_cpp_invalid_or_unavailable_backend_is_rejected() -> None:
    provider = LlamaCppDecisionProvider(LlamaCppConfig())

    with patch("urllib.request.urlopen", side_effect=OSError("server offline")):
        decision = provider.decide(_state(), _goal())

    assert decision.status is DecisionStatus.REJECTED
    assert decision.action is None
    assert decision.confidence == 0.0
    assert decision.provider == "llama.cpp-local"

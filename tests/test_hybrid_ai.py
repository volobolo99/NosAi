from app.ai.hybrid import HybridOrchestrator


class StubProvider:
    def __init__(self, result=None, error=None):
        self.result = result or {}
        self.error = error
        self.calls = 0

    def decide(self, state, objective):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


def test_high_confidence_uses_local_without_openai():
    local = StubProvider({"action_type": "move", "valid": True, "confidence": 0.95})
    remote = StubProvider({"action_type": "heal", "valid": True, "confidence": 0.9})
    orchestrator = HybridOrchestrator(local, remote)

    result = orchestrator.decide({}, "farm")

    assert result.provider == "local"
    assert result.fallback_used is False
    assert remote.calls == 0


def test_low_confidence_routes_to_openai():
    local = StubProvider({"action_type": "move", "valid": True, "confidence": 0.30})
    remote = StubProvider({"action_type": "heal", "valid": True, "confidence": 0.91})
    orchestrator = HybridOrchestrator(local, remote)

    result = orchestrator.decide({}, "survive", strategic=False)

    assert result.provider == "openai"
    assert result.action_type == "heal"
    assert result.fallback_used is False


def test_strategic_request_routes_to_openai():
    local = StubProvider({"action_type": "move", "valid": True, "confidence": 0.99})
    remote = StubProvider({"action_type": "plan", "valid": True, "confidence": 0.88})
    orchestrator = HybridOrchestrator(local, remote)

    result = orchestrator.decide({}, "plan route", strategic=True)

    assert result.provider == "openai"
    assert remote.calls == 1


def test_openai_failure_falls_back_to_local():
    local = StubProvider({"action_type": "move", "valid": True, "confidence": 0.80})
    remote = StubProvider(error=RuntimeError("network down"))
    orchestrator = HybridOrchestrator(local, remote)

    result = orchestrator.decide({}, "farm", strategic=True)

    assert result.provider == "local"
    assert result.fallback_used is True
    assert result.action_type == "move"
    assert "network down" in result.error

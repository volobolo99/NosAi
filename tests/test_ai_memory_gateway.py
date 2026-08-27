import asyncio

from app.ai.contracts import ActionIntent, ActionKind, Decision
from app.ai.gateway import AIGateway
from app.safety.ai_gate import validate_ai_decision


class Provider:
    async def decide(self, context):
        return Decision(ActionIntent(ActionKind.WAIT), 0.8, "test")


class FailingProvider:
    async def decide(self, context):
        raise RuntimeError("provider unavailable")


def test_gateway_uses_provider():
    result = asyncio.run(AIGateway(Provider(), Provider()).decide({}))
    assert result.fallback_used is False
    assert result.decision.selected.kind is ActionKind.WAIT


def test_gateway_fails_over_to_deterministic_provider():
    result = asyncio.run(AIGateway(FailingProvider(), Provider()).decide({}))
    assert result.fallback_used is True


def test_safety_is_proposal_only_when_live_actions_disabled():
    decision = Decision(ActionIntent(ActionKind.ATTACK), 0.9, "test")
    result = validate_ai_decision(decision, observation_valid=True, live_actions_enabled=False)
    assert result["status"] == "PROPOSAL_ONLY"


def test_safety_rejects_invalid_observation():
    decision = Decision(ActionIntent(ActionKind.ATTACK), 0.9, "test")
    result = validate_ai_decision(decision, observation_valid=False, live_actions_enabled=True)
    assert result["status"] == "REJECTED"
    assert result["action"] == "noop"

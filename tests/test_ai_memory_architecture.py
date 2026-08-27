import pytest

from app.ai.contracts import ActionIntent, ActionKind, Decision, MemoryRecord, Goal, Outcome, RewardEvidence
from app.ai.openai_provider import DeterministicFallbackProvider
from app.memory.intelligent_facade import IntelligentMemory


@pytest.mark.asyncio
async def test_deterministic_fallback_is_safe_wait():
    result = await DeterministicFallbackProvider().decide({})
    assert result.selected.kind is ActionKind.WAIT
    assert result.confidence == 0.0


@pytest.mark.asyncio
async def test_memory_rejects_unknown_namespace():
    class Store:
        async def write(self, namespace, record):
            pass
        async def search(self, query, limit=20):
            return []

    memory = IntelligentMemory(Store())
    record = MemoryRecord("fp", Goal("test"), ActionIntent(ActionKind.WAIT), Outcome("ok"), RewardEvidence())
    with pytest.raises(ValueError):
        await memory.remember("unknown", record)

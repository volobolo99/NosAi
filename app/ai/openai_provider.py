"""Provider boundary for OpenAI-backed reasoning.

This module intentionally contains no live API call yet. The concrete OpenAI
client belongs behind this adapter and must be configured server-side.
"""
from __future__ import annotations

from app.ai.contracts import ActionIntent, ActionKind, Decision


class OpenAIReasoningProvider:
    """Translate structured NosAi context into a provider decision.

    The transport/client is injected so tests never require credentials or
    network access. Live integration is enabled only by the composition root.
    """

    name = "openai"

    def __init__(self, client=None):
        self._client = client

    async def decide(self, context: dict) -> Decision:
        if self._client is None:
            raise RuntimeError("OpenAI provider is not configured")
        # Concrete Responses API mapping is intentionally isolated here.
        raise NotImplementedError("Bind the project-approved OpenAI client adapter")


class DeterministicFallbackProvider:
    name = "deterministic-fallback"

    async def decide(self, context: dict) -> Decision:
        return Decision(ActionIntent(ActionKind.WAIT), 0.0, "AI unavailable; deterministic safe fallback")

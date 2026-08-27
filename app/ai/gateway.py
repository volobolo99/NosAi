"""Provider-neutral AI gateway boundary for NosAi.

The gateway owns orchestration concerns (timeout, fallback, provenance), while
provider adapters remain isolated. It never executes game actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.ai.contracts import Decision


class DecisionProvider(Protocol):
    async def decide(self, context: dict) -> Decision: ...


@dataclass(frozen=True)
class GatewayResult:
    decision: Decision
    provider: str
    fallback_used: bool = False


class AIGateway:
    def __init__(self, provider: DecisionProvider, fallback: DecisionProvider) -> None:
        self._provider = provider
        self._fallback = fallback

    async def decide(self, context: dict) -> GatewayResult:
        try:
            decision = await self._provider.decide(context)
            return GatewayResult(decision, provider=type(self._provider).__name__)
        except Exception:
            decision = await self._fallback.decide(context)
            return GatewayResult(decision, provider=type(self._fallback).__name__, fallback_used=True)

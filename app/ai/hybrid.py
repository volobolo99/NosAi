"""Hybrid local/OpenAI orchestration for NosAi.

The orchestrator chooses a provider for a decision but never executes the
resulting game action. Action transport remains a separately gated boundary.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Mapping

from .providers import AIProvider


@dataclass(frozen=True)
class HybridDecision:
    """Decision plus routing metadata suitable for logs/evaluation."""

    action_type: str | None
    valid: bool
    confidence: float
    provider: str
    fallback_used: bool
    latency_ms: float
    rationale: str = ""
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type,
            "valid": self.valid,
            "confidence": self.confidence,
            "provider": self.provider,
            "fallback_used": self.fallback_used,
            "latency_ms": self.latency_ms,
            "rationale": self.rationale,
            "error": self.error,
        }


class HybridOrchestrator:
    """Route between local and OpenAI providers with safe local fallback.

    Local is the default for real-time decisions. OpenAI is selected when the
    caller explicitly requests strategic reasoning or when local confidence is
    below the configured threshold. If OpenAI fails, the local result is kept.
    """

    def __init__(
        self,
        local: AIProvider,
        openai: AIProvider | None = None,
        *,
        confidence_threshold: float = 0.70,
    ):
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")
        self.local = local
        self.openai = openai
        self.confidence_threshold = confidence_threshold

    def decide(
        self,
        state: Mapping[str, Any],
        objective: str,
        *,
        strategic: bool = False,
    ) -> HybridDecision:
        started = time.perf_counter()
        local_error: str | None = None
        try:
            local_result = dict(self.local.decide(state, objective))
        except Exception as exc:
            local_result = {"valid": False, "confidence": 0.0, "action_type": None}
            local_error = f"{type(exc).__name__}: {exc}"

        confidence = float(local_result.get("confidence", 0.0))
        use_openai = self.openai is not None and (strategic or confidence < self.confidence_threshold)

        if not use_openai:
            return self._decision(
                local_result,
                provider="local",
                fallback_used=False,
                started=started,
                error=local_error,
            )

        try:
            remote_result = dict(self.openai.decide(state, objective))
            return self._decision(
                remote_result,
                provider="openai",
                fallback_used=False,
                started=started,
                error=None,
            )
        except Exception as exc:
            # OpenAI is an enhancement path, never a single point of failure.
            return self._decision(
                local_result,
                provider="local",
                fallback_used=True,
                started=started,
                error=f"OpenAI {type(exc).__name__}: {exc}",
            )

    @staticmethod
    def _decision(
        result: Mapping[str, Any],
        *,
        provider: str,
        fallback_used: bool,
        started: float,
        error: str | None,
    ) -> HybridDecision:
        return HybridDecision(
            action_type=result.get("action_type"),
            valid=bool(result.get("valid", result.get("action_type") is not None)),
            confidence=max(0.0, min(1.0, float(result.get("confidence", 0.0)))),
            provider=provider,
            fallback_used=fallback_used,
            latency_ms=(time.perf_counter() - started) * 1000,
            rationale=str(result.get("rationale", "")),
            error=error,
        )

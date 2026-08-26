"""Provider boundaries for the NosAi hybrid AI runtime.

The OpenAI provider is deliberately separated from the local provider so the
real-time game loop can remain local and deterministic when required.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Mapping, Protocol


class AIProvider(Protocol):
    """Minimal provider contract used by the hybrid orchestrator."""

    name: str

    def decide(self, state: Mapping[str, Any], objective: str) -> Mapping[str, Any]:
        """Return a normalized decision without executing a game action."""


@dataclass(frozen=True)
class ProviderResult:
    """Normalized provider result used by orchestration and evaluation."""

    action_type: str | None
    valid: bool
    confidence: float
    rationale: str = ""
    provider: str = "unknown"
    raw: Mapping[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type,
            "valid": self.valid,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "provider": self.provider,
        }


class LocalAIProvider:
    """Adapter around a local decision callable.

    The callable is injected by the local model/runtime layer. This keeps the
    orchestration contract independent of a specific local model framework.
    """

    name = "local"

    def __init__(self, decision_fn):
        self._decision_fn = decision_fn

    def decide(self, state: Mapping[str, Any], objective: str) -> Mapping[str, Any]:
        result = dict(self._decision_fn(state, objective))
        result.setdefault("provider", self.name)
        return result


class OpenAIProvider:
    """OpenAI Responses API adapter for strategic/non-real-time reasoning."""

    name = "openai"

    def __init__(self, model: str | None = None, client: Any | None = None):
        self.model = model or os.getenv("NOSAI_OPENAI_MODEL", "gpt-5.6-luna")
        self._client = client

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:  # pragma: no cover - environment dependent
                raise RuntimeError(
                    "OpenAI provider requires the optional 'openai' dependency."
                ) from exc
            self._client = OpenAI()
        return self._client

    def decide(self, state: Mapping[str, Any], objective: str) -> Mapping[str, Any]:
        prompt = (
            "You are the strategic reasoning component of NosAi for a NosTale client. "
            "Do not execute actions. Return ONLY valid JSON with keys: action_type, "
            "valid, confidence, rationale. Use conservative decisions when state is "
            "uncertain.\n\n"
            f"Objective: {objective}\n"
            f"State: {json.dumps(dict(state), ensure_ascii=False, sort_keys=True)}"
        )
        response = self._get_client().responses.create(model=self.model, input=prompt)
        text = getattr(response, "output_text", "")
        try:
            result = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("OpenAI returned non-JSON decision output") from exc
        result["provider"] = self.name
        return result

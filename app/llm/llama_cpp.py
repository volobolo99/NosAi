"""Local llama.cpp HTTP decision provider.

The adapter is deliberately proposal-only: it can produce a typed Decision but
never executes actions or mutates runtime state. The llama.cpp server is an
optional local dependency; the NosAi package itself remains dependency-free.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping
from uuid import uuid4

from app.core.contracts import (
    CandidateAction,
    Decision,
    DecisionStatus,
    Goal,
    Risk,
    WorldState,
)


@dataclass(frozen=True)
class LlamaCppConfig:
    base_url: str = "http://127.0.0.1:8080"
    model: str = "local"
    timeout_seconds: float = 15.0
    max_tokens: int = 512
    temperature: float = 0.0

    @classmethod
    def from_env(cls) -> "LlamaCppConfig":
        return cls(
            base_url=os.getenv("NOSAI_LLAMA_CPP_URL", cls.base_url).rstrip("/"),
            model=os.getenv("NOSAI_LLAMA_CPP_MODEL", cls.model),
            timeout_seconds=float(os.getenv("NOSAI_LLAMA_CPP_TIMEOUT", cls.timeout_seconds)),
            max_tokens=int(os.getenv("NOSAI_LLAMA_CPP_MAX_TOKENS", cls.max_tokens)),
            temperature=float(os.getenv("NOSAI_LLAMA_CPP_TEMPERATURE", cls.temperature)),
        )

    def __post_init__(self) -> None:
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must use http:// or https://")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")


class LlamaCppDecisionProvider:
    """DecisionProvider backed by a local llama.cpp OpenAI-compatible server."""

    name = "llama.cpp-local"

    def __init__(self, config: LlamaCppConfig | None = None) -> None:
        self.config = config or LlamaCppConfig.from_env()

    def decide(self, state: WorldState, goal: Goal) -> Decision:
        prompt = self._build_prompt(state, goal)
        try:
            payload = self._complete(prompt)
            return self._decision_from_payload(payload)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            return Decision(
                decision_id=f"llama-error-{uuid4().hex}",
                status=DecisionStatus.REJECTED,
                action=None,
                rationale=f"Local provider unavailable or invalid response: {exc}",
                confidence=0.0,
                provider=self.name,
                model=self.config.model,
            )

    def _complete(self, prompt: str) -> Mapping[str, Any]:
        request_body = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return JSON only. Never execute actions. Propose at most one action. "
                        "Schema: {status,rationale,confidence,action}. action is null for noop/rejected; "
                        "otherwise {action_id,action_type,parameters,risk}."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        data = json.dumps(request_body).encode("utf-8")
        request = urllib.request.Request(
            f"{self.config.base_url}/v1/chat/completions",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise OSError(f"llama.cpp HTTP {exc.code}") from exc
        envelope = json.loads(raw)
        content = envelope["choices"][0]["message"]["content"]
        if isinstance(content, str):
            content = json.loads(content)
        if not isinstance(content, Mapping):
            raise TypeError("model content must be a JSON object")
        return content

    def _decision_from_payload(self, payload: Mapping[str, Any]) -> Decision:
        status = DecisionStatus(str(payload.get("status", "rejected")).lower())
        confidence = float(payload.get("confidence", 0.0))
        rationale = str(payload.get("rationale", ""))
        action_data = payload.get("action")
        action = None
        if action_data is not None:
            if not isinstance(action_data, Mapping):
                raise TypeError("action must be an object or null")
            risk_data = action_data.get("risk", {})
            if not isinstance(risk_data, Mapping):
                raise TypeError("risk must be an object")
            action = CandidateAction(
                action_id=str(action_data["action_id"]),
                action_type=str(action_data["action_type"]),
                parameters=dict(action_data.get("parameters", {})),
                risk=Risk(
                    score=float(risk_data.get("score", 1.0)),
                    category=str(risk_data.get("category", "unknown")),
                    rationale=str(risk_data.get("rationale", "")),
                ),
            )
        if status is DecisionStatus.NOOP:
            action = None
        return Decision(
            decision_id=f"llama-{uuid4().hex}",
            status=status,
            action=action,
            rationale=rationale,
            confidence=confidence,
            provider=self.name,
            model=self.config.model,
        )

    @staticmethod
    def _build_prompt(state: WorldState, goal: Goal) -> str:
        state_values = json.dumps(dict(state.values), sort_keys=True, default=str)
        return (
            "Evaluate the observed state against the goal. Stay within the supplied state; "
            "do not invent facts. Produce a proposal only.\n"
            f"state_id={state.state_id}\n"
            f"state_confidence={state.confidence}\n"
            f"state_values={state_values}\n"
            f"goal_id={goal.goal_id}\n"
            f"objective={goal.objective}\n"
            f"priority={goal.priority}"
        )

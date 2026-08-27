"""Stable routing boundary between NosAi and a local secondary AI.

The router does not ship or select a concrete model yet. It provides the
contract that the future local runtime will implement, while allowing the
orchestrator, AutoSet and benchmark layers to discover its state safely.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Protocol


class LocalAIStatus(str, Enum):
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    READY = "ready"
    BUSY = "busy"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class LocalAIRequest:
    prompt: str
    task: str = "general"
    max_latency_ms: int | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class LocalAIResult:
    text: str
    model: str
    latency_ms: float
    confidence: float | None = None
    metadata: Mapping[str, Any] | None = None


class LocalAIBackend(Protocol):
    """Contract implemented later by Ollama/llama.cpp/ONNX/etc. adapters."""

    def status(self) -> LocalAIStatus: ...

    def generate(self, request: LocalAIRequest) -> LocalAIResult: ...

    def health(self) -> Mapping[str, Any]: ...


class SecondaryAIRouter:
    """Integration point for the local secondary AI.

    Policy is deliberately conservative: the secondary model is opt-in and
    cannot silently replace the primary orchestrator until a later milestone
    defines routing, confidence, safety and benchmark gates.
    """

    def __init__(self, backend: LocalAIBackend | None = None, enabled: bool = False):
        self._backend = backend
        self.enabled = enabled

    def status(self) -> LocalAIStatus:
        if not self.enabled:
            return LocalAIStatus.DISABLED
        if self._backend is None:
            return LocalAIStatus.UNAVAILABLE
        return self._backend.status()

    def health(self) -> Mapping[str, Any]:
        if self._backend is None:
            return {"status": self.status().value}
        return dict(self._backend.health())

    def generate(self, request: LocalAIRequest) -> LocalAIResult:
        if not self.enabled or self._backend is None:
            raise RuntimeError("Local secondary AI is not configured")
        return self._backend.generate(request)

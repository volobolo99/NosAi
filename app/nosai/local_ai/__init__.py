"""Local secondary AI subsystem for NosAi.

This package defines the stable integration boundary for a future on-device
model. The concrete inference backend is intentionally decoupled from the
main orchestration layer so it can be developed and benchmarked independently.
"""

from .router import LocalAIRequest, LocalAIResult, LocalAIStatus, SecondaryAIRouter

__all__ = [
    "LocalAIRequest",
    "LocalAIResult",
    "LocalAIStatus",
    "SecondaryAIRouter",
]

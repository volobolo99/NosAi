"""Select a conservative perception/runtime backend from detected capabilities."""

from __future__ import annotations

from dataclasses import dataclass

from .capabilities import HardwareProfile


@dataclass(frozen=True)
class RuntimeSelection:
    capture_backend: str
    inference_backend: str
    acceleration: str
    local_ai_enabled: bool
    reason: str


def select_runtime(profile: HardwareProfile) -> RuntimeSelection:
    if profile.os_name == "Windows":
        capture = "dxcam"
        if profile.gpu_name:
            return RuntimeSelection(
                capture_backend=capture,
                inference_backend="onnx-runtime",
                acceleration="gpu-preferred",
                local_ai_enabled=True,
                reason="Windows GPU detected; use DXGI capture and accelerated local inference when available.",
            )
        return RuntimeSelection(
            capture_backend=capture,
            inference_backend="onnx-runtime",
            acceleration="cpu",
            local_ai_enabled=True,
            reason="Windows detected without a confirmed GPU; use CPU-safe local inference.",
        )

    return RuntimeSelection(
        capture_backend="generic",
        inference_backend="onnx-runtime",
        acceleration="cpu",
        local_ai_enabled=True,
        reason="Non-Windows fallback runtime.",
    )

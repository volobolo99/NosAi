"""Select the safest available local/remote AI runtime."""
from __future__ import annotations

from dataclasses import dataclass

from .capabilities import HardwareProfile


@dataclass(frozen=True)
class RuntimeSelection:
    capture: str
    perception: str
    reasoning: str
    openai_enabled: bool
    mode: str


def select_runtime(profile: HardwareProfile) -> RuntimeSelection:
    if profile.os_name == "Windows" and profile.capture_backend == "dxcam":
        capture = "dxcam"
    else:
        capture = "portable-fallback"

    perception = "torch-cuda" if profile.cuda_available else "torch-cpu" if profile.torch_available else "cpu"
    openai_enabled = profile.openai_key_present
    reasoning = "hybrid" if openai_enabled else "local-only"
    mode = "optimal" if profile.os_name == "Windows" and (profile.cuda_available or profile.torch_available) else "compatibility"
    return RuntimeSelection(capture, perception, reasoning, openai_enabled, mode)

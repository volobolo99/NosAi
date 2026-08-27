"""Portable hardware profile and conservative local-model policy."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HardwareProfile:
    ram_gb: float
    vram_gb: float = 0.0
    cpu_threads: int = 0
    gpu_name: str = ""


def recommend_local_model(profile: HardwareProfile) -> str:
    # Conservative baseline: preserve responsiveness for game automation.
    if profile.vram_gb >= 20 and profile.ram_gb >= 32:
        return "qwen3:14b"
    if profile.vram_gb >= 8 and profile.ram_gb >= 16:
        return "qwen3:8b"
    return "qwen3:4b"

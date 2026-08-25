"""Hardware-aware defaults for the target NosAi laptop.

The project is designed to run alongside the game, so online decision-making stays
CPU-first while larger offline learning jobs can use the CUDA GPU when available.
All values are conservative and can be overridden by callers.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class HardwareProfile:
    """Conservative execution profile for a 16 GB RAM / 8 GB VRAM laptop."""

    cpu_threads: int
    worker_threads: int
    ram_budget_gb: float = 8.0
    vram_budget_gb: float = 6.5
    online_device: str = "cpu"
    training_device: str = "cpu"
    gpu_training_min_samples: int = 256

    @classmethod
    def detect(cls) -> "HardwareProfile":
        cpu_threads = max(1, int(os.cpu_count() or 4))
        worker_threads = min(6, max(2, cpu_threads // 2))
        training_device = "cpu"
        try:
            import torch
            if torch.cuda.is_available():
                training_device = "cuda"
        except ImportError:
            pass
        return cls(
            cpu_threads=cpu_threads,
            worker_threads=worker_threads,
            training_device=training_device,
        )


def detect_hardware() -> HardwareProfile:
    """Return the current machine profile without requiring PyTorch."""
    return HardwareProfile.detect()

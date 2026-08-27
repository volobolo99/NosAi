"""Safe local hardware detection, benchmark planning, and AutoSet state.

The service is intentionally side-effect-light: it records a profile and a
recommended model, but never enables live game actions.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from app.runtime.hardware_profile import HardwareProfile, recommend_local_model


class AutoConfigurator:
    def __init__(self, state_path: str | None = None) -> None:
        self.state_path = Path(state_path or os.getenv("NOSAI_AUTOCONFIG_STATE", "data/autoconfig.json"))

    def detect(self) -> HardwareProfile:
        ram_gb = 0.0
        try:
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
        except Exception:
            pass
        return HardwareProfile(ram_gb=ram_gb, gpu_name=platform.processor(), cpu_threads=os.cpu_count() or 0)

    def ollama_available(self) -> bool:
        return shutil.which("ollama") is not None

    def benchmark(self, profile: HardwareProfile | None = None) -> dict:
        profile = profile or self.detect()
        model = recommend_local_model(profile)
        result = {"model": model, "hardware": asdict(profile), "ollama_available": self.ollama_available(), "benchmark_status": "recommended_only"}
        if self.ollama_available():
            start = time.perf_counter()
            try:
                proc = subprocess.run(["ollama", "show", model], capture_output=True, text=True, timeout=15, check=False)
                result["model_installed"] = proc.returncode == 0
                result["probe_ms"] = round((time.perf_counter() - start) * 1000, 1)
                result["benchmark_status"] = "probe_complete"
            except (OSError, subprocess.SubprocessError):
                result["model_installed"] = False
        return result

    def autoset(self) -> dict:
        result = self.benchmark()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        os.environ["NOSAI_LOCAL_MODEL"] = result["model"]
        return result

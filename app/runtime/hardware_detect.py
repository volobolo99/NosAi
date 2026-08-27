"""Best-effort hardware detection used by AutoSet.

Detection is advisory and has no side effects on game execution.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess

from app.runtime.hardware_profile import HardwareProfile


def detect_hardware() -> HardwareProfile:
    ram_gb = 0.0
    try:
        import psutil
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        pass

    gpu_name = ""
    vram_gb = 0.0
    if platform.system() == "Windows":
        try:
            p = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_VideoController | Select-Object -First 1 Name,AdapterRAM | ConvertTo-Json -Compress"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            import json
            data = json.loads(p.stdout) if p.stdout else {}
            gpu_name = str(data.get("Name", ""))
            vram_gb = round(float(data.get("AdapterRAM", 0)) / (1024 ** 3), 1)
        except Exception:
            pass

    return HardwareProfile(
        ram_gb=ram_gb,
        vram_gb=vram_gb,
        cpu_threads=os.cpu_count() or 0,
        gpu_name=gpu_name or platform.processor(),
    )


def ollama_executable() -> str | None:
    return shutil.which("ollama")

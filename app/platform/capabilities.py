"""Best-effort Windows hardware/runtime capability detection.

The detector is deliberately dependency-light: it can run before optional AI
packages are installed and never makes optional acceleration mandatory.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class HardwareProfile:
    os_name: str
    os_version: str
    python_version: str
    machine: str
    cpu_count: int
    ram_gb: float | None
    gpu_vendor: str | None
    gpu_name: str | None
    gpu_vram_mb: int | None
    npu_present: bool | None
    directx_available: bool | None
    windows_graphics_available: bool | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _powershell(command: str) -> str | None:
    if os.name != "nt" or not shutil.which("powershell"):
        return None
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if completed.returncode == 0:
            return completed.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def _gpu_info() -> tuple[str | None, str | None, int | None]:
    output = _powershell(
        "Get-CimInstance Win32_VideoController | "
        "Select-Object Name,AdapterCompatibility,AdapterRAM | "
        "ConvertTo-Json -Compress"
    )
    if not output:
        return None, None, None
    try:
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]
        if not data:
            return None, None, None
        # Prefer a controller with the largest reported VRAM.
        item = max(data, key=lambda x: int(x.get("AdapterRAM") or 0))
        ram = item.get("AdapterRAM")
        return (
            item.get("AdapterCompatibility"),
            item.get("Name"),
            int(ram / (1024 * 1024)) if ram else None,
        )
    except (ValueError, TypeError, KeyError):
        return None, None, None


def _npu_present() -> bool | None:
    output = _powershell(
        "Get-PnpDevice -PresentOnly | "
        "Where-Object { $_.FriendlyName -match 'NPU|Neural|AI Boost|AI Accelerator' } | "
        "Select-Object -First 1 FriendlyName | ConvertTo-Json -Compress"
    )
    if output:
        return True
    return None if os.name != "nt" else False


def detect_hardware_profile() -> HardwareProfile:
    vendor, gpu_name, gpu_vram_mb = _gpu_info()
    ram_gb: float | None = None
    try:
        import psutil

        ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    except (ImportError, AttributeError, OSError):
        pass

    return HardwareProfile(
        os_name=platform.system(),
        os_version=platform.version(),
        python_version=platform.python_version(),
        machine=platform.machine(),
        cpu_count=os.cpu_count() or 1,
        ram_gb=ram_gb,
        gpu_vendor=vendor,
        gpu_name=gpu_name,
        gpu_vram_mb=gpu_vram_mb,
        npu_present=_npu_present(),
        directx_available=True if os.name == "nt" else False,
        windows_graphics_available=True if os.name == "nt" else False,
    )
"""Capability discovery with safe fallbacks.

The detector is intentionally observational: it never changes drivers, GPU settings,
or Windows configuration. Results are used to select an appropriate runtime.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
import platform
import shutil
import subprocess
import sys
from typing import Any


@dataclass(frozen=True)
class HardwareProfile:
    os_name: str
    os_version: str
    architecture: str
    python_version: str
    cpu_count: int
    ram_gb: float | None
    gpu_names: tuple[str, ...]
    npu_detected: bool
    directx_available: bool
    capture_backend: str
    cuda_available: bool
    torch_available: bool
    openai_key_present: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def _windows_gpu_names() -> tuple[str, ...]:
    if platform.system() != "Windows":
        return ()
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"],
            capture_output=True, text=True, timeout=3, check=False,
        )
        return tuple(x.strip() for x in result.stdout.splitlines() if x.strip())
    except (OSError, subprocess.SubprocessError):
        return ()


def _ram_gb() -> float | None:
    try:
        if platform.system() == "Windows":
            import ctypes
            class MemoryStatus(ctypes.Structure):
                _fields_ = [("length", ctypes.c_uint32), ("memory_load", ctypes.c_uint32),
                            ("total", ctypes.c_uint64), ("available", ctypes.c_uint64),
                            ("total_page", ctypes.c_uint64), ("available_page", ctypes.c_uint64),
                            ("total_virtual", ctypes.c_uint64), ("available_virtual", ctypes.c_uint64),
                            ("available_extended", ctypes.c_uint64)]
            status = MemoryStatus()
            status.length = ctypes.sizeof(MemoryStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return round(status.total / (1024 ** 3), 2)
        if hasattr(os, "sysconf"):
            return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / (1024 ** 3), 2)
    except (AttributeError, OSError, ValueError):
        pass
    return None


def _torch_info() -> tuple[bool, bool]:
    try:
        import torch  # type: ignore
        return True, bool(torch.cuda.is_available())
    except ImportError:
        return False, False


def detect_hardware_profile() -> HardwareProfile:
    system = platform.system()
    torch_available, cuda_available = _torch_info()
    directx = system == "Windows" and shutil.which("dxdiag") is not None
    gpu_names = _windows_gpu_names()
    npu = any("NPU" in name.upper() or "NEURAL" in name.upper() for name in gpu_names)
    return HardwareProfile(
        os_name=system,
        os_version=platform.version(),
        architecture=platform.machine(),
        python_version=sys.version.split()[0],
        cpu_count=os.cpu_count() or 1,
        ram_gb=_ram_gb(),
        gpu_names=gpu_names,
        npu_detected=npu,
        directx_available=directx,
        capture_backend="dxcam" if system == "Windows" else "portable-fallback",
        cuda_available=cuda_available,
        torch_available=torch_available,
        openai_key_present=bool(os.getenv("OPENAI_API_KEY")),
    )

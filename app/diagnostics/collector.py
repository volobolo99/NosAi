"""Collect hardware, Windows, display, Python and NosTale observations.

The collector is intentionally read-only and uses only standard-library APIs.
It never reads credentials, browser data, game memory, or network packets.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from app.client.nostale_windows import WindowsNosTaleAdapter


def _powershell_json(script: str) -> Any:
    if os.name != "nt":
        return None
    try:
        raw = subprocess.check_output(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _memory_bytes() -> int | None:
    if os.name != "nt":
        return None
    try:
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong),
                ("memory_load", ctypes.c_ulong),
                ("total_phys", ctypes.c_ulonglong),
                ("avail_phys", ctypes.c_ulonglong),
                ("total_page", ctypes.c_ulonglong),
                ("avail_page", ctypes.c_ulonglong),
                ("total_virtual", ctypes.c_ulonglong),
                ("avail_virtual", ctypes.c_ulonglong),
                ("avail_extended", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.length = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return int(status.total_phys)
    except (AttributeError, OSError):
        pass
    return None


def _windows_info() -> dict[str, Any]:
    version = platform.win32_ver()
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "build": sys.getwindowsversion().build if os.name == "nt" else None,
        "edition": platform.win32_edition(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "win32_version": version,
    }


def _hardware_info() -> dict[str, Any]:
    script = (
        "$cs=Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model,TotalPhysicalMemory; "
        "$cpu=Get-CimInstance Win32_Processor | Select-Object -First 1 Name,NumberOfCores,NumberOfLogicalProcessors; "
        "$gpu=Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,AdapterRAM; "
        "[pscustomobject]@{Computer=$cs;CPU=$cpu;GPU=@($gpu)} | ConvertTo-Json -Depth 4"
    )
    data = _powershell_json(script)
    if not isinstance(data, dict):
        return {"query_ok": False}
    computer = data.get("Computer") or {}
    cpu = data.get("CPU") or {}
    gpus = data.get("GPU") or []
    if isinstance(gpus, dict):
        gpus = [gpus]
    return {
        "query_ok": True,
        "manufacturer": computer.get("Manufacturer"),
        "model": computer.get("Model"),
        "total_memory_bytes": _memory_bytes() or computer.get("TotalPhysicalMemory"),
        "cpu": cpu,
        "gpus": gpus,
    }


def collect_diagnostics() -> dict[str, Any]:
    """Return a privacy-safe snapshot useful for NosAi hardware/runtime tuning."""
    adapter = WindowsNosTaleAdapter()
    result: dict[str, Any] = {
        "schema": "nosai.diagnostics.v1",
        "timestamp_unix": time.time(),
        "windows": _windows_info(),
        "hardware": _hardware_info(),
        "environment": {
            "cwd": str(Path.cwd()),
            "python_executable": sys.executable,
        },
        "nostale": {
            "connected": False,
            "state_read": False,
            "process_names": list(adapter.process_names),
            "observation_only": True,
            "action_transport": "disabled",
        },
    }
    try:
        result["nostale"]["connected"] = adapter.check_connection()
        if result["nostale"]["connected"]:
            result["nostale"]["state"] = adapter.read_state().payload
            result["nostale"]["state_read"] = True
    except Exception as exc:  # diagnostics must report, never crash on client absence
        result["nostale"]["error"] = {"type": type(exc).__name__, "message": str(exc)}
    return result


def write_report(path: str | Path, report: dict[str, Any]) -> Path:
    """Write deterministic, UTF-8 JSON diagnostics to *path*."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target

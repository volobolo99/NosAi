"""Read-only Windows runtime adapter.

This adapter is deliberately an observation boundary: it discovers the local
NosTale process and exposes hardware/runtime facts to NosAi without injecting
code, sending input, patching memory, or changing the operating system.
"""
from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import asdict, dataclass
from typing import Any

from app.autoset import autoset
from app.hardware_profile import detect_hardware


@dataclass(frozen=True)
class RuntimeSnapshot:
    os: str
    python: str
    cpu_threads: int
    worker_threads: int
    online_device: str
    training_device: str
    client_detected: bool
    client_pids: tuple[int, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _find_nostale_processes() -> tuple[int, ...]:
    if os.name != "nt":
        return ()
    try:
        completed = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ()
    found: list[int] = []
    for line in completed.stdout.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) < 2:
            continue
        image_name = parts[0].lower()
        if "nostale" not in image_name:
            continue
        try:
            found.append(int(parts[1]))
        except ValueError:
            continue
    return tuple(sorted(set(found)))


def snapshot() -> RuntimeSnapshot:
    hw = detect_hardware()
    pids = _find_nostale_processes()
    return RuntimeSnapshot(
        os=platform.platform(),
        python=platform.python_version(),
        cpu_threads=hw.cpu_threads,
        worker_threads=hw.worker_threads,
        online_device=hw.online_device,
        training_device=hw.training_device,
        client_detected=bool(pids),
        client_pids=pids,
    )


def prepare(*, benchmark: bool = True) -> dict[str, Any]:
    """Prepare a runtime session using AutoSet and return an auditable snapshot."""
    result = autoset(benchmark=benchmark)
    result["runtime"] = snapshot().to_dict()
    result["mode"] = "READ_ONLY_OBSERVATION"
    result["capabilities"] = {
        "process_discovery": True,
        "hardware_detection": True,
        "benchmark": benchmark,
        "input_injection": False,
        "memory_write": False,
        "code_injection": False,
        "os_configuration": False,
    }
    return result


__all__ = ["RuntimeSnapshot", "prepare", "snapshot"]

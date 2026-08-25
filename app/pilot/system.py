"""Non-sensitive local runtime profiling for Test Pilot diagnostics."""

from __future__ import annotations

import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def collect_system_profile() -> dict[str, Any]:
    """Collect only runtime characteristics useful for performance diagnostics."""
    return {
        "schema_version": "nosai.system_profile.v1",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "executable": sys.executable,
    }


def write_system_profile(profile: dict[str, Any], path: str | Path) -> Path:
    """Serialize a runtime profile to the requested diagnostic artifact path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")
    return target

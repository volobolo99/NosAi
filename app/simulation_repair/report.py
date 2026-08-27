"""Machine-readable report sealing for simulation evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .models import SimulationRun


def seal_report(run: SimulationRun, directory: str | Path) -> dict[str, Any]:
    if not run.sealed:
        raise ValueError("Simulation run must be sealed before report export")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    payload = run.to_dict()
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    report_path = root / f"{run.run_id}.json"
    report_path.write_bytes(raw)
    manifest = {"run_id": run.run_id, "sha256": digest, "report": report_path.name, "schema": "simulation-report-v1"}
    (root / f"{run.run_id}.manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {**manifest, "path": str(report_path)}

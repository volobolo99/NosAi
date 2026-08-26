from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = ROOT / ".nosai" / "test-center" / "latest.json"


def load_ci_evidence() -> dict[str, Any]:
    if not EVIDENCE_PATH.exists():
        return {"status": "NOT_RUN", "source": str(EVIDENCE_PATH)}
    try:
        data = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "source": str(EVIDENCE_PATH), "error": f"{type(exc).__name__}: {exc}"}
    if not isinstance(data, dict):
        return {"status": "FAIL", "source": str(EVIDENCE_PATH), "error": "CI evidence root must be an object"}
    data["source"] = str(EVIDENCE_PATH)
    return data

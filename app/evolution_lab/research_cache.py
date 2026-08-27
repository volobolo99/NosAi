"""Content-addressed cache for normalized online research findings."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from .research import ResearchResult


def cache_key(query: str) -> str:
    return hashlib.sha256(query.strip().encode("utf-8")).hexdigest()


def save_result(root: Path, result: ResearchResult) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    destination = root / f"{cache_key(result.query)}.json"
    payload = {"query": result.query, "findings": [asdict(finding) for finding in result.findings]}
    destination.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return destination

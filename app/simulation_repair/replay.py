"""Small, deterministic replay store for protected regression scenarios."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True, slots=True)
class ReplayCase:
    case_id: str
    scenario: dict[str, Any]
    expected: dict[str, Any]
    protected: bool = True

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:24]


class ReplayStore:
    """Append-only JSONL store; protected cases cannot be silently removed."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, case: ReplayCase) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(case), sort_keys=True, ensure_ascii=True) + "\n")

    def load(self) -> list[ReplayCase]:
        if not self.path.exists():
            return []
        cases: list[ReplayCase] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    raw = json.loads(line)
                    cases.append(ReplayCase(**raw))
        return cases

    def protected(self) -> list[ReplayCase]:
        return [case for case in self.load() if case.protected]


def anti_forgetting_gate(baseline: dict[str, float], candidate: dict[str, float], *, tolerance: float = 0.0) -> tuple[bool, list[str]]:
    """Require protected scenario scores not to regress beyond tolerance."""
    regressions = [
        key for key, old in baseline.items()
        if key in candidate and candidate[key] < old - tolerance
    ]
    return (not regressions, regressions)

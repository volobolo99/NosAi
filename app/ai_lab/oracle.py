from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class OracleResult:
    status: str
    safety_status: str
    reason_codes: tuple[str, ...]


def evaluate_oracle(*, world_state: Mapping[str, Any], decision: str | None, available_actions: Sequence[str], forbidden_actions: Sequence[str] = (), preferred_actions: Sequence[str] = (), acceptable_actions: Sequence[str] = ()) -> OracleResult:
    if decision is None:
        return OracleResult("NOT_RUN", "NOT_RUN", ("NO_DECISION",))
    reasons: list[str] = []
    safety = "PASS"
    available = set(available_actions)
    forbidden = set(forbidden_actions)
    if decision not in available:
        reasons.append("INVALID_ACTION")
    if decision in forbidden:
        safety = "FAIL"
        reasons.append("FORBIDDEN_ACTION")
    hp = world_state.get("hp_ratio")
    if isinstance(hp, (int, float)) and hp <= 0.15 and "retreat" in available and decision != "retreat":
        reasons.append("CRITICAL_HP_PRIORITY")
    elif preferred_actions and decision not in set(preferred_actions) and decision not in set(acceptable_actions):
        reasons.append("STRATEGIC_MISMATCH")
    status = "PASS" if safety == "PASS" and not reasons else "FAIL"
    if safety == "PASS" and "STRATEGIC_MISMATCH" in reasons:
        status = "SAFE-BUT-DIFFERENT"
    return OracleResult(status, safety, tuple(reasons))

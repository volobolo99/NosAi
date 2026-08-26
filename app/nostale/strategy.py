"""Source-grounded NosTale strategy signals for offline/runtime decision layers.

The strategic rules in this module are intentionally conservative. They encode the
attached *Guida Strategica e Analisi NosTale* as explicit, inspectable signals rather
than hiding game assumptions inside a neural model. The source should be treated as
an engineering hypothesis until live observations or authoritative references verify
individual mechanics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from app.reward.engine import RewardContext


class RoomObjective(StrEnum):
    KILL_ALL = "kill_all"
    SURVIVAL = "survival"
    TARGET_ELIMINATION = "target_elimination"
    SWITCH_ACCESS = "switch_access"
    ESCORT = "escort"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class HardcoreRaidState:
    team_lives_pool: int = 0
    damage_contributed: float = 0.0
    contribution_required: bool = False

    def __post_init__(self) -> None:
        if self.team_lives_pool < 0:
            raise ValueError("team_lives_pool cannot be negative")
        if self.damage_contributed < 0:
            raise ValueError("damage_contributed cannot be negative")


@dataclass(frozen=True, slots=True)
class NosTaleState:
    """Normalized state fields suggested by the attached strategy document."""

    hp_ratio: float = 1.0
    mp_ratio: float = 1.0
    dignity: int = 0
    grade_differential: int = 0
    effective_res_down: float = 0.0
    target_resist_net: float = 0.0
    target_distance: float = 0.0
    target_type: int = 0
    time_remaining_sec: int = 0
    fairy_element_pct: float = 0.0
    elemental_energy: float = 0.0
    sp_attack: int = 0
    sp_element: int = 0
    s_percent_damage: float = 0.0
    hardcore: HardcoreRaidState | None = None
    room_objective: RoomObjective = RoomObjective.UNKNOWN

    def __post_init__(self) -> None:
        if not 0.0 <= self.hp_ratio <= 1.0:
            raise ValueError("hp_ratio must be between 0 and 1")
        if not 0.0 <= self.mp_ratio <= 1.0:
            raise ValueError("mp_ratio must be between 0 and 1")
        if not -1000 <= self.dignity <= 100:
            raise ValueError("dignity must be between -1000 and 100")
        if self.time_remaining_sec < 0:
            raise ValueError("time_remaining_sec cannot be negative")
        if self.target_distance < 0:
            raise ValueError("target_distance cannot be negative")


@dataclass(frozen=True, slots=True)
class StrategicAssessment:
    resistance_break_critical: bool
    dignity_guard: bool
    low_hp_guard: bool
    raid_risk_high: bool
    recommended_focus: str
    reward_adjustments: Mapping[str, float] = field(default_factory=dict)
    rationale: tuple[str, ...] = ()


def assess_strategy(state: NosTaleState) -> StrategicAssessment:
    """Turn source rules into transparent priorities for a planner/reward layer."""
    resistance_break_critical = state.target_resist_net >= 1.0
    dignity_guard = state.dignity < -400
    low_hp_guard = state.hp_ratio < 0.30
    raid_risk_high = bool(state.hardcore and state.hardcore.team_lives_pool <= 2)

    if state.room_objective is RoomObjective.SURVIVAL:
        focus = "survive_and_position"
    elif state.room_objective is RoomObjective.TARGET_ELIMINATION:
        focus = "primary_target_burst"
    elif state.room_objective is RoomObjective.SWITCH_ACCESS:
        focus = "switch_access_with_aggro_control"
    elif state.room_objective is RoomObjective.ESCORT:
        focus = "protect_escort_target"
    elif resistance_break_critical:
        focus = "break_resistance_threshold"
    else:
        focus = "efficient_damage"

    adjustments: dict[str, float] = {}
    rationale: list[str] = []

    if resistance_break_critical:
        adjustments["resistance_threshold"] = 10.0
        rationale.append("target net resistance is at/above the source's 100% elemental threshold")
    if dignity_guard:
        adjustments["dignity_guard"] = 8.0
        rationale.append("dignity is below -400; the source associates this range with functional restrictions")
    if low_hp_guard:
        adjustments["survival"] = 6.0
        rationale.append("low HP should increase defensive/consumable priority")
    if raid_risk_high:
        adjustments["hardcore_life_preservation"] = 12.0
        rationale.append("hardcore raid life pool is critically low")
    if state.room_objective is RoomObjective.KILL_ALL:
        rationale.append("kill-all room favors clustering and AoE according to the source")
    elif state.room_objective is RoomObjective.SURVIVAL:
        rationale.append("survival room favors kiting and edge positioning according to the source")
    elif state.room_objective is RoomObjective.TARGET_ELIMINATION:
        rationale.append("target-elimination room favors single-target focus according to the source")

    return StrategicAssessment(
        resistance_break_critical=resistance_break_critical,
        dignity_guard=dignity_guard,
        low_hp_guard=low_hp_guard,
        raid_risk_high=raid_risk_high,
        recommended_focus=focus,
        reward_adjustments=adjustments,
        rationale=tuple(rationale),
    )


def build_reward_context(
    state: NosTaleState,
    *,
    intrinsic_reward: float = 0.0,
    goal_progress: float = 0.0,
    success: bool = False,
    duration_seconds: float = 0.0,
    resources_used: float = 0.0,
    failed: bool = False,
    metadata: Mapping[str, Any] | None = None,
) -> RewardContext:
    """Create a reward context enriched with explicit NosTale strategy signals."""
    assessment = assess_strategy(state)
    risk = 0.0
    if assessment.dignity_guard:
        risk += 1.0
    if assessment.low_hp_guard:
        risk += 1.0
    if assessment.raid_risk_high:
        risk += 2.0

    merged = dict(metadata or {})
    merged.update(
        {
            "recommended_focus": assessment.recommended_focus,
            "resistance_break_critical": assessment.resistance_break_critical,
            "dignity_guard": assessment.dignity_guard,
            "room_objective": state.room_objective.value,
            "source_basis": "Guida Strategica e Analisi NosTale.pdf",
        }
    )
    return RewardContext(
        goal_progress=goal_progress,
        success=success,
        intrinsic_reward=intrinsic_reward,
        duration_seconds=duration_seconds,
        risk=risk,
        resources_used=resources_used,
        failed=failed,
        metadata=merged,
    )

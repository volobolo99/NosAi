"""Deterministic GameState invariants and contradiction diagnostics."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .game_state import GameState


@dataclass(frozen=True)
class StateIssue:
    code: str
    severity: str
    message: str
    entity_id: int | None = None


@dataclass(frozen=True)
class StateValidation:
    issues: tuple[StateIssue, ...]

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "ERROR" for issue in self.issues)

    @property
    def errors(self) -> int:
        return sum(issue.severity == "ERROR" for issue in self.issues)

    @property
    def warnings(self) -> int:
        return sum(issue.severity == "WARNING" for issue in self.issues)


def validate_game_state(state: GameState) -> StateValidation:
    issues: list[StateIssue] = []
    player = state.player

    if player.entity_id is not None and player.entity_id <= 0:
        issues.append(StateIssue("PLAYER_ID_INVALID", "ERROR", "player entity_id must be positive", player.entity_id))

    if player.hp is not None and player.hp < 0:
        issues.append(StateIssue("PLAYER_HP_NEGATIVE", "ERROR", "player hp cannot be negative", player.entity_id))
    if player.hp_max is not None and player.hp_max <= 0:
        issues.append(StateIssue("PLAYER_HP_MAX_INVALID", "ERROR", "player hp_max must be positive", player.entity_id))
    if player.hp is not None and player.hp_max is not None and player.hp > player.hp_max:
        issues.append(StateIssue("PLAYER_HP_OVER_MAX", "ERROR", "player hp exceeds hp_max", player.entity_id))

    if player.mp is not None and player.mp < 0:
        issues.append(StateIssue("PLAYER_MP_NEGATIVE", "ERROR", "player mp cannot be negative", player.entity_id))
    if player.mp_max is not None and player.mp_max <= 0:
        issues.append(StateIssue("PLAYER_MP_MAX_INVALID", "ERROR", "player mp_max must be positive", player.entity_id))
    if player.mp is not None and player.mp_max is not None and player.mp > player.mp_max:
        issues.append(StateIssue("PLAYER_MP_OVER_MAX", "ERROR", "player mp exceeds mp_max", player.entity_id))

    for label, value in (("player_x", player.x), ("player_y", player.y)):
        if value is not None and not math.isfinite(value):
            issues.append(StateIssue("PLAYER_COORDINATE_NONFINITE", "ERROR", f"{label} must be finite", player.entity_id))

    for entity_id, entity in state.world.entities.items():
        if entity_id <= 0:
            issues.append(StateIssue("ENTITY_ID_INVALID", "ERROR", "entity id must be positive", entity_id))
        if entity.x is not None and not math.isfinite(entity.x):
            issues.append(StateIssue("ENTITY_X_NONFINITE", "ERROR", "entity x must be finite", entity_id))
        if entity.y is not None and not math.isfinite(entity.y):
            issues.append(StateIssue("ENTITY_Y_NONFINITE", "ERROR", "entity y must be finite", entity_id))
        if entity.confidence < 0.0 or entity.confidence > 1.0:
            issues.append(StateIssue("ENTITY_CONFIDENCE_INVALID", "ERROR", "entity confidence must be in [0,1]", entity_id))

    if state.revision < 0 or player.revision < 0 or state.world.revision < 0:
        issues.append(StateIssue("REVISION_INVALID", "ERROR", "state revisions cannot be negative"))

    if state.revision < player.revision + state.world.revision:
        issues.append(StateIssue("REVISION_INCONSISTENT", "WARNING", "aggregate revision is lower than component revisions"))

    return StateValidation(tuple(issues))

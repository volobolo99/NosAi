"""Deterministic/stochastic combat primitives from the NosAi architecture spec.

This module is a simulator only. It consumes explicit state inputs and returns
predictions; it never attaches to, injects into, or sends actions to a client.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from random import Random
from typing import Sequence


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class SkillTiming:
    cast_time: float
    animation_duration: float
    cooldown: float

    def __post_init__(self) -> None:
        if min(self.cast_time, self.animation_duration, self.cooldown) < 0:
            raise ValueError("skill timings cannot be negative")


class BCardPriority(IntEnum):
    HARD_CC = 0
    STAT_DEBUFF = 1
    DOT = 2
    CLEANSE = 99


@dataclass(frozen=True)
class BCardEffect:
    name: str
    priority: BCardPriority
    level: int = 0
    duration_ticks: int = 0
    magnitude: float = 0.0
    source: str = "skill"


class BCardFSM:
    """Priority-aware effect state machine matching the architecture table."""

    def __init__(self) -> None:
        self._effects: list[BCardEffect] = []
        self.cast_active = False

    @property
    def effects(self) -> tuple[BCardEffect, ...]:
        return tuple(self._effects)

    @property
    def hard_cc(self) -> bool:
        return any(e.priority == BCardPriority.HARD_CC for e in self._effects)

    def apply(self, effect: BCardEffect) -> None:
        if effect.priority == BCardPriority.CLEANSE:
            self._effects = [e for e in self._effects if e.level > effect.level]
            return
        if effect.priority == BCardPriority.HARD_CC:
            self.cast_active = False
        if effect.priority == BCardPriority.STAT_DEBUFF:
            same_name = [e for e in self._effects if e.name == effect.name]
            if same_name and max(e.level for e in same_name) >= effect.level:
                return
            self._effects = [e for e in self._effects if e.name != effect.name]
        self._effects.append(effect)
        self._effects.sort(key=lambda e: (int(e.priority), -e.level))

    def tick(self) -> tuple[BCardEffect, ...]:
        next_effects = []
        expired = []
        for effect in self._effects:
            remaining = effect.duration_ticks - 1 if effect.duration_ticks > 0 else effect.duration_ticks
            if effect.duration_ticks > 0 and remaining <= 0:
                expired.append(effect)
            else:
                next_effects.append(
                    BCardEffect(effect.name, effect.priority, effect.level, remaining, effect.magnitude, effect.source)
                )
        self._effects = next_effects
        return tuple(expired)


@dataclass(frozen=True)
class AttackInput:
    accuracy: float
    attacker_morale: float
    target_morale: float
    target_evasion: float
    base_attack: float
    equipment_attack: float
    target_defense: float
    shell_penetration: float
    elemental_attack: float
    elemental_stat: float
    fairy_percent: float
    shell_element_bonus_percent: float
    target_resistance: float
    resistance_reduction: float
    elemental_advantage: float = 0.0
    critical_multiplier: float = 1.0
    s_damage_multiplier: float = 1.0


@dataclass(frozen=True)
class AttackResult:
    hit_probability: float
    hit: bool
    physical_damage: float
    elemental_damage: float
    total_damage: float
    elemental_multiplier: float


class CombatSimulator:
    """Implements the architecture's atomic combat chain."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = Random(seed)

    def simulate_attack(self, data: AttackInput, forced_roll: float | None = None) -> AttackResult:
        if data.target_evasion <= 0:
            raise ValueError("target_evasion must be positive")
        morale_delta = data.attacker_morale - data.target_morale
        hit_probability = clamp((data.accuracy + morale_delta) / data.target_evasion, 0.20, 1.00)
        roll = self._rng.random() if forced_roll is None else forced_roll
        if not 0.0 <= roll <= 1.0:
            raise ValueError("forced_roll must be in [0, 1]")
        if roll > hit_probability:
            return AttackResult(hit_probability, False, 0.0, 0.0, 0.0, 0.0)

        physical = max(
            1.0,
            data.base_attack + data.equipment_attack
            - data.target_defense * (1.0 - clamp(data.shell_penetration, 0.0, 1.0)),
        )
        fairy_multiplier = (data.fairy_percent + data.shell_element_bonus_percent) / 100.0
        elemental_attack = (data.elemental_attack + data.elemental_stat * 10.0) * fairy_multiplier
        net_resistance = data.target_resistance - data.resistance_reduction
        elemental_multiplier = 1.0 + data.elemental_advantage - net_resistance / 100.0
        elemental = max(0.0, elemental_attack * elemental_multiplier)
        total = (physical + elemental) * data.critical_multiplier * data.s_damage_multiplier * self._rng.uniform(0.95, 1.05)
        return AttackResult(hit_probability, True, physical, elemental, total, elemental_multiplier)

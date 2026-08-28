"""Source-derived unified NosMate Pet + cognitive Partner domain model.

The design is adapted from the uploaded ``Modulo Unificato NosMate e Partner
System.tex``. The document is treated as a design specification; gameplay
mechanics remain hypotheses until validated by runtime observations.

This module intentionally stays independent of Unity and of the live-client
adapter. It exposes deterministic state, memory, affinity, SP-skill cooldowns,
and tactical decision signals that can be consumed by the existing runtime.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
import random
from typing import Any, Mapping


class RelationshipTier(str, Enum):
    STRANGER = "STRANGER"
    ALLY = "ALLY"
    TRUSTED = "TRUSTED"
    CORE_PARTNER = "CORE_PARTNER"


class SkillRank(str, Enum):
    F = "F"
    E = "E"
    D = "D"
    C = "C"
    B = "B"
    A = "A"
    S = "S"


class BehaviorState(str, Enum):
    TEAM_SUPPORT = "TEAM_SUPPORT"
    DEFENSIVE_SELF = "DEFENSIVE_SELF"
    HESITATE_OR_RETREAT = "HESITATE_OR_RETREAT"
    RETREAT_SELF_HEAL = "RETREAT_SELF_HEAL"


class PartyCommand(str, Enum):
    SUPPORT_PLAYER = "support_player"
    ATTACK = "attack"
    FLANK = "flank"
    RETREAT = "retreat"
    HIGH_RISK = "high_risk"


class CommandRisk(str, Enum):
    STANDARD = "standard"
    HIGH = "high"


@dataclass
class PartnerSPSkill:
    skill_id: str
    skill_name: str
    rank: SkillRank = SkillRank.C
    cooldown: float = 10.0
    current_cooldown: float = 0.0

    def __post_init__(self) -> None:
        if self.cooldown < 0:
            raise ValueError("cooldown cannot be negative")
        if self.current_cooldown < 0:
            raise ValueError("current_cooldown cannot be negative")

    @property
    def is_ready(self) -> bool:
        return self.current_cooldown <= 0.0

    def tick(self, delta_seconds: float) -> None:
        if delta_seconds < 0:
            raise ValueError("delta_seconds cannot be negative")
        self.current_cooldown = max(0.0, self.current_cooldown - delta_seconds)

    def trigger(self) -> None:
        self.current_cooldown = self.cooldown


@dataclass
class SpecialistPartnerCard:
    sp_id: str
    sp_name: str
    element: str
    skills: list[PartnerSPSkill] = field(default_factory=list)
    is_equipped: bool = False

    def first_ready_skill(self) -> PartnerSPSkill | None:
        if not self.is_equipped:
            return None
        return next((skill for skill in self.skills if skill.is_ready), None)


@dataclass(frozen=True)
class MemoryEvent:
    description: str
    impact: float
    target: str = "trust"
    age_seconds: float = 0.0

    def impact_at(self, age_seconds: float, decay_lambda: float) -> float:
        if age_seconds < 0:
            raise ValueError("age_seconds cannot be negative")
        if decay_lambda < 0:
            raise ValueError("decay_lambda cannot be negative")
        return self.impact * math.exp(-decay_lambda * age_seconds)


@dataclass
class PartnerMemory:
    """Short/long-term memory model from the specification.

    Events whose absolute initial impact is at least 30 are consolidated into
    long-term traits and permanently affect their selected relationship axis.
    Lower-impact events remain in short-term memory and decay exponentially.
    """

    consolidation_threshold: float = 30.0
    decay_lambda: float = 0.01
    short_term_events: list[MemoryEvent] = field(default_factory=list)
    long_term_traits: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.consolidation_threshold < 0:
            raise ValueError("consolidation_threshold cannot be negative")
        if self.decay_lambda < 0:
            raise ValueError("decay_lambda cannot be negative")

    def register(self, event: MemoryEvent) -> bool:
        if event.target not in {"trust", "affection"}:
            raise ValueError("event target must be 'trust' or 'affection'")
        if abs(event.impact) >= self.consolidation_threshold:
            self.long_term_traits.append(event.description)
            return True
        self.short_term_events.append(event)
        return False

    def decayed_short_term_impact(self, age_seconds: float) -> float:
        return sum(
            event.impact_at(age_seconds + event.age_seconds, self.decay_lambda)
            for event in self.short_term_events
        )


@dataclass(frozen=True)
class PartnerEquipment:
    weapon_damage: float = 0.0
    armor_defense: float = 0.0
    resistances: Mapping[str, float] = field(default_factory=dict)


@dataclass
class PartnerEntity:
    partner_id: str
    name: str
    archetype: str
    health: float = 100.0
    max_health: float = 100.0
    stamina: float = 100.0
    morale: float = 80.0
    trust: float = 75.0
    affection: float = 60.0
    alpha_trust: float = 0.6
    equipment: PartnerEquipment = field(default_factory=PartnerEquipment)
    active_sp: SpecialistPartnerCard | None = None
    memory: PartnerMemory = field(default_factory=PartnerMemory)
    behavior_state: BehaviorState = BehaviorState.TEAM_SUPPORT

    def __post_init__(self) -> None:
        if self.max_health <= 0:
            raise ValueError("max_health must be positive")
        if not 0.0 <= self.alpha_trust <= 1.0:
            raise ValueError("alpha_trust must be between 0 and 1")
        for name in ("health", "stamina", "morale", "trust", "affection"):
            value = getattr(self, name)
            if not 0.0 <= value <= 100.0:
                raise ValueError(f"{name} must be between 0 and 100")
        self.health = min(self.health, self.max_health)

    @property
    def beta_affection(self) -> float:
        return 1.0 - self.alpha_trust

    @property
    def affinity(self) -> float:
        return self.alpha_trust * self.trust + self.beta_affection * self.affection

    @property
    def relationship_tier(self) -> RelationshipTier:
        affinity = self.affinity
        if affinity >= 81.0:
            return RelationshipTier.CORE_PARTNER
        if affinity >= 51.0:
            return RelationshipTier.TRUSTED
        if affinity >= 21.0:
            return RelationshipTier.ALLY
        return RelationshipTier.STRANGER

    @property
    def health_ratio(self) -> float:
        return self.health / self.max_health

    @property
    def decision_weight(self) -> float:
        return self.morale * 0.6 + self.trust * 0.4

    def obedience_probability(self, stress_battle: float) -> float:
        if stress_battle < 0:
            raise ValueError("stress_battle cannot be negative")
        stress_factor = max(0.0, 1.0 - stress_battle / 200.0)
        return (self.affinity / 100.0) * (self.morale / 100.0) * stress_factor

    def should_obey_high_risk(self, stress_battle: float, rng: random.Random | None = None) -> bool:
        generator = rng or random.Random()
        return generator.random() <= self.obedience_probability(stress_battle)

    def evaluate_behavior(self) -> BehaviorState:
        if self.health_ratio < 0.20 or self.morale < 15.0:
            return BehaviorState.RETREAT_SELF_HEAL
        if self.decision_weight >= 60.0:
            return BehaviorState.TEAM_SUPPORT
        if self.decision_weight >= 40.0:
            return BehaviorState.DEFENSIVE_SELF
        return BehaviorState.HESITATE_OR_RETREAT

    def tick(self, delta_seconds: float) -> None:
        if delta_seconds < 0:
            raise ValueError("delta_seconds cannot be negative")
        if self.active_sp is not None:
            for skill in self.active_sp.skills:
                skill.tick(delta_seconds)
        self.behavior_state = self.evaluate_behavior()

    def use_ready_sp_skill(self) -> PartnerSPSkill | None:
        if self.active_sp is None:
            return None
        skill = self.active_sp.first_ready_skill()
        if skill is None:
            return None
        skill.trigger()
        return skill

    def register_memory_event(self, event: MemoryEvent) -> bool:
        consolidated = self.memory.register(event)
        if consolidated:
            if event.target == "trust":
                self.trust = min(100.0, max(0.0, self.trust + event.impact))
            else:
                self.affection = min(100.0, max(0.0, self.affection + event.impact))
        return consolidated

    def tactical_command(self, command: PartyCommand, stress_battle: float = 0.0) -> str:
        self.behavior_state = self.evaluate_behavior()
        if command is PartyCommand.HIGH_RISK and not self.should_obey_high_risk(stress_battle):
            return "REFUSE_HIGH_RISK_COMMAND"
        if self.behavior_state is BehaviorState.RETREAT_SELF_HEAL:
            return "RETREAT_SELF_HEAL"
        if self.behavior_state is BehaviorState.TEAM_SUPPORT:
            return command.value
        if self.behavior_state is BehaviorState.DEFENSIVE_SELF:
            return "DEFENSIVE_SELF"
        return "HESITATE_OR_RETREAT"


@dataclass(frozen=True)
class PartySignal:
    signal: str
    source: str = "CoordinatedActionManager"
    payload: Mapping[str, Any] = field(default_factory=dict)


class PartnerDecisionEvaluator:
    """Deterministic priority evaluator matching the document's decision tree."""

    def evaluate(
        self,
        partner: PartnerEntity,
        *,
        player_health_ratio: float = 1.0,
        party_signal: PartySignal | None = None,
    ) -> str:
        if not 0.0 <= player_health_ratio <= 1.0:
            raise ValueError("player_health_ratio must be between 0 and 1")
        state = partner.evaluate_behavior()
        if state is BehaviorState.RETREAT_SELF_HEAL:
            return "RETREAT_SELF_HEAL"

        skill = partner.active_sp.first_ready_skill() if partner.active_sp else None
        if skill is not None:
            return f"USE_SP_SKILL:{skill.skill_id}"

        if player_health_ratio < 0.30 and partner.decision_weight >= 60.0:
            return "RESCUE_PLAYER"

        if party_signal is not None and party_signal.signal == "NOSMATE_COMBO":
            return "SYNCHRONIZED_FLANK_OR_DISTRACTION"

        if state is BehaviorState.TEAM_SUPPORT:
            return "MAINTAIN_TACTICAL_POSITION"
        if state is BehaviorState.DEFENSIVE_SELF:
            return "DEFENSIVE_SELF"
        return "HESITATE_OR_RETREAT"


def build_partner_snapshot(partner: PartnerEntity) -> dict[str, Any]:
    """Return a JSON-compatible representation of the domain state."""
    return {
        "partner_id": partner.partner_id,
        "name": partner.name,
        "archetype": partner.archetype,
        "stats": {
            "health": partner.health,
            "max_hp": partner.max_health,
            "current_hp": partner.health,
            "stamina": partner.stamina,
            "morale": partner.morale,
            "trust": partner.trust,
            "affection": partner.affection,
        },
        "personality_weights": {
            "alpha_trust": partner.alpha_trust,
            "beta_affection": partner.beta_affection,
        },
        "relationship_tier": partner.relationship_tier.value,
        "equipment": {
            "weapon_damage": partner.equipment.weapon_damage,
            "armor_defense": partner.equipment.armor_defense,
            "resistances": dict(partner.equipment.resistances),
        },
        "specialist_card": None
        if partner.active_sp is None
        else {
            "is_equipped": partner.active_sp.is_equipped,
            "sp_id": partner.active_sp.sp_id,
            "sp_name": partner.active_sp.sp_name,
            "element": partner.active_sp.element,
            "skills": [
                {
                    "skill_id": skill.skill_id,
                    "name": skill.skill_name,
                    "skill_rank": skill.rank.value,
                    "cooldown": skill.cooldown,
                    "current_cooldown": skill.current_cooldown,
                }
                for skill in partner.active_sp.skills
            ],
        },
        "memory": {
            "short_term_events": [event.description for event in partner.memory.short_term_events],
            "long_term_traits": list(partner.memory.long_term_traits),
        },
        "behavior_state": partner.behavior_state.value,
    }

from __future__ import annotations

import random

import pytest

from app.party.nosmate_partner import (
    BehaviorState,
    MemoryEvent,
    PartnerDecisionEvaluator,
    PartnerEntity,
    PartnerSPSkill,
    PartySignal,
    RelationshipTier,
    SkillRank,
    SpecialistPartnerCard,
    build_partner_snapshot,
)


def make_partner() -> PartnerEntity:
    return PartnerEntity(
        partner_id="partner_kliff_01",
        name="Kliff",
        archetype="Melee Tank / Frontliner",
        health=8500.0,
        max_health=8500.0,
        morale=80.0,
        trust=75.0,
        affection=60.0,
        active_sp=SpecialistPartnerCard(
            sp_id="sp_aegir_01",
            sp_name="Aegir the Viking",
            element="WATER",
            is_equipped=True,
            skills=[
                PartnerSPSkill("aegir_buff", "Viking Protection", SkillRank.S, 40.0),
                PartnerSPSkill("aegir_taunt", "Immortal Roar", SkillRank.A, 15.0),
            ],
        ),
    )


def test_affinity_and_relationship_tier_follow_specification() -> None:
    partner = make_partner()
    assert partner.affinity == pytest.approx(69.0)
    assert partner.relationship_tier is RelationshipTier.TRUSTED
    assert partner.decision_weight == pytest.approx(74.0)


def test_critical_health_has_priority_over_team_support() -> None:
    partner = make_partner()
    partner.health = 1000.0
    assert partner.evaluate_behavior() is BehaviorState.RETREAT_SELF_HEAL
    assert PartnerDecisionEvaluator().evaluate(partner) == "RETREAT_SELF_HEAL"


def test_sp_skill_has_independent_cooldown() -> None:
    partner = make_partner()
    skill = partner.use_ready_sp_skill()
    assert skill is not None
    assert skill.skill_id == "aegir_buff"
    assert skill.current_cooldown == pytest.approx(40.0)
    partner.tick(10.0)
    assert skill.current_cooldown == pytest.approx(30.0)


def test_memory_consolidates_at_absolute_impact_30() -> None:
    partner = make_partner()
    consolidated = partner.register_memory_event(
        MemoryEvent("SAVED_PLAYER_IN_RAID", 30.0, target="trust")
    )
    assert consolidated is True
    assert partner.trust == pytest.approx(100.0)
    assert "SAVED_PLAYER_IN_RAID" in partner.memory.long_term_traits


def test_low_impact_memory_decays_exponentially() -> None:
    partner = make_partner()
    partner.register_memory_event(MemoryEvent("MINOR_EVENT", 10.0, target="affection"))
    assert partner.memory.decayed_short_term_impact(0.0) == pytest.approx(10.0)
    assert partner.memory.decayed_short_term_impact(100.0) == pytest.approx(10.0 * 2.718281828**-1, rel=1e-6)


def test_high_risk_obedience_is_seedable_and_bounded() -> None:
    partner = make_partner()
    probability = partner.obedience_probability(0.0)
    assert 0.0 <= probability <= 1.0
    assert partner.should_obey_high_risk(0.0, random.Random(1)) is True


def test_decision_tree_prioritizes_player_rescue_after_sp_is_on_cooldown() -> None:
    partner = make_partner()
    partner.use_ready_sp_skill()
    assert PartnerDecisionEvaluator().evaluate(partner, player_health_ratio=0.2) == "RESCUE_PLAYER"


def test_decision_tree_consumes_nosmate_combo_signal() -> None:
    partner = make_partner()
    for skill in partner.active_sp.skills:
        skill.trigger()
    result = PartnerDecisionEvaluator().evaluate(
        partner,
        party_signal=PartySignal("NOSMATE_COMBO"),
    )
    assert result == "SYNCHRONIZED_FLANK_OR_DISTRACTION"


def test_snapshot_matches_document_shape() -> None:
    snapshot = build_partner_snapshot(make_partner())
    assert snapshot["partner_id"] == "partner_kliff_01"
    assert snapshot["relationship_tier"] == "TRUSTED"
    assert snapshot["specialist_card"]["sp_id"] == "sp_aegir_01"
    assert len(snapshot["specialist_card"]["skills"]) == 2

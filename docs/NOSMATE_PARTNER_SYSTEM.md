# NosMate Party System — runtime integration

## Source basis

This module is the runtime-domain adaptation of the uploaded **Modulo Unificato NosMate e Partner System.tex**. The source defines a unified party composed of Player, Pet (NosMate) and Partner, with Partner affinity, short/long-term memory, equipment, Specialist Partner cards and a priority-based tactical evaluator.

The source specification explicitly describes Trust + Affection affinity, STP/LTP memory, independent SP cooldowns, relationship tiers, a decision weight based on Morale + Trust, high-risk command obedience, and a priority tree covering self-preservation, SP skills, player rescue, NosMate synchronization and tactical positioning.

## Runtime mapping

| Source concept | NosAi runtime implementation |
| --- | --- |
| Trust + Affection | `PartnerEntity.affinity` |
| Relationship tiers | `RelationshipTier` |
| Morale + Trust decision weight | `PartnerEntity.decision_weight` |
| SP Partner + 3+ skills | `SpecialistPartnerCard` + `PartnerSPSkill` |
| Independent cooldowns | `PartnerSPSkill.tick()` / `trigger()` |
| STP/LTP | `PartnerMemory` + `MemoryEvent` |
| 30-point consolidation threshold | `PartnerMemory.consolidation_threshold` |
| High-risk command obedience | `obedience_probability()` / `should_obey_high_risk()` |
| Decision tree | `PartnerDecisionEvaluator` |
| CoordinatedActionManager signal | `PartySignal("NOSMATE_COMBO")` |
| JSON entity shape | `build_partner_snapshot()` |

## Architectural boundary

The implementation is deliberately Python-native and engine-agnostic. It does **not** introduce Unity dependencies, live-client input, memory injection, or autonomous game actions. It exposes state and decisions to the existing NosAi runtime so a later adapter can connect them to perception, planning and action layers.

The source document's gameplay mechanics are treated as design hypotheses until validated against observations or authoritative references, consistent with the repository's source-grounded strategy policy.

## Validation

`tests/test_nosmate_partner.py` covers:

- affinity and relationship tiers;
- critical-health priority;
- SP cooldown behavior;
- STP → LTP consolidation;
- exponential memory decay;
- deterministic/seedable high-risk obedience;
- player rescue priority;
- NosMate synchronization signals;
- JSON-compatible snapshots.

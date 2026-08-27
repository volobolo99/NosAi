# NosAi — CharacterSnapshot Contract

Versioned read-only representation of the NosTale character state consumed by PlayAi and GuardAi.

## Identity/context

- snapshot_id
- schema_version
- timestamp
- server/channel/context
- character level/class
- progression milestones

## Combat/progression

- base and effective stats
- equipment and upgrade state
- specialist state
- skills and relevant progression
- resistances/bonuses where known
- PvE/PvP capability indicators
- active objectives

## Economy/resources

- Gold/resources known to the runtime
- consumables/materials
- inventory summary
- expected income rates
- resource bottlenecks

## Activity state

- current activity
- quest/raid/activity progress
- cooldowns/timers when available
- recent outcomes/replay references

## Derived fields

Derived fields must be explicitly marked and reproducible:

- progression_score
- bottleneck candidates
- estimated farming efficiency
- target distance
- confidence/data-quality

## Privacy/security

No credentials, payment data, authentication secrets or unnecessary personal information. The snapshot is read-only and must be validated against its schema before use.

## Versioning

Every snapshot records schema and source versions. Consumers must reject incompatible major versions rather than silently interpreting fields.

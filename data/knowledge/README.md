# NosAi Knowledge Graph

This directory is the persistent home for the Bug/Glitch Research knowledge layer.

## Design goals

- Evidence-first: every claim can carry source URL, version, observation time and confidence.
- Version-aware: game versions belong in node properties/evidence and can later become explicit `version` nodes.
- Graph-native: bugs, glitches, packets, events, states, maps, quests, skills, items, tests and fixes can be linked.
- Local-first: SQLite is used initially, so the feature works without an external database service.
- Migration-friendly: `schema_version` is included in JSON export/import.

## Storage

The default runtime database is `data/knowledge/nosai_knowledge.sqlite3` and is created on first use.

The database should not be committed when it contains local observations or user-specific runtime data.

## Core relations

Relations are deliberately strings rather than a closed enum so new NosTale concepts can be added without a schema migration. Recommended initial relations include:

- `SUPPORTED_BY`
- `INVOLVES`
- `OBSERVED_IN`
- `TRIGGERED_BY`
- `CAUSES`
- `CONTRADICTS`
- `REPRODUCED_BY`
- `FIXED_BY`
- `AFFECTS`
- `OCCURS_ON_VERSION`

## Safety boundary

The knowledge layer stores research evidence and reproducibility metadata. It does not itself send packets, alter a game client, or automate interaction with a server. Those capabilities remain separate so that evidence collection can be audited and controlled.

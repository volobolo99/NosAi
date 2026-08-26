# Static data ingestion

Static NosTale knowledge is stored as versioned records with provenance.

Supported categories include items, skills, monsters, maps, NPCs, translations,
and other immutable/reference data.

Rules:

1. Never overwrite an existing source record silently.
2. Preserve source, version and retrieval metadata.
3. Unknown fields are retained in `fields`.
4. A source is not treated as authoritative merely because it is online.
5. Live promotion requires validation against the current client or a trusted schema.
6. Imported data must remain replayable and attributable.

This allows NosAi to combine static knowledge with real-client observations without
turning an external database into an unverified source of truth.

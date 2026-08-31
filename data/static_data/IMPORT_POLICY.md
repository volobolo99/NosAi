# Static knowledge import policy

NosAi never treats an online value as verified merely because it exists.

## Required provenance

Every imported record must retain:

- source identifier/URL;
- source version or commit when available;
- retrieval timestamp;
- record kind and stable identifier;
- transformation/import version.

## Verification tiers

- `observed`: captured from the real client or an authenticated replay;
- `schema_verified`: field meaning is supported by a maintained packet/data schema;
- `source_verified`: static value comes from a traceable source;
- `promoted`: explicitly accepted after validation/tests.

Only promoted records may be consumed as authoritative static knowledge by the live decision layer.

Unknown fields remain unknown. Conflicting sources are stored separately rather than silently merged.

## Source priority

1. Real-client observations/replays.
2. Versioned NosCore packet/data definitions.
3. Maintained ecosystem implementations such as NosSmooth.
4. Other community references, only as non-authoritative candidates.

No scraper is allowed to overwrite verified data automatically.

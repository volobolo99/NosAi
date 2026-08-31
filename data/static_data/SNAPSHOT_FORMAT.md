# Source snapshot format

Every imported source can be pinned by `source_id`, `source_ref`, optional version/commit, and a deterministic SHA-256 of the normalized payload.

The digest is calculated from canonical JSON (sorted keys and stable separators), so equivalent payloads produce the same digest. A changed upstream source therefore becomes a new snapshot rather than silently replacing previous knowledge.

Snapshots are metadata, not proof of semantic correctness: verification and promotion gates still apply.

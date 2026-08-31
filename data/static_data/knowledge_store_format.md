# Promoted knowledge store

Promoted records are written as deterministic JSONL. Each record retains its kind,
canonical fields and source provenance. Ordering is stable by kind, record id and
source id so generated snapshots can be compared reproducibly.

Only records returned by the promotion gate should be written here. Candidate and
quarantined records remain outside the AI-readable store.

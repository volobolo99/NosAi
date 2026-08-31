# Static knowledge import pipeline

1. Fetch a source at a pinned URL/ref/commit.
2. Normalize into `KnowledgeCandidate`.
3. Preserve source id, reference, version and commit.
4. Detect field-level conflicts across sources.
5. Reject or quarantine conflicting/unverified candidates.
6. Promote only verified records into the AI-readable knowledge set.

No source wins merely because it is newer or larger. Conflicts require explicit
validation against a stronger source or real-client observation.

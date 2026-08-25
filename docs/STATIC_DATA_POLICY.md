# NosAi static-data acquisition policy

NosAi must not depend on hand-filled placeholder game data when a machine-readable source can be obtained.

## Source order

1. **Current local NosTale client data** — highest priority for version accuracy.
2. **Official/first-party online API or documentation** — preferred when machine-readable and versioned.
3. **Public community API/provider** — accepted with provenance, version and checksum metadata.
4. **Public community repository** — fallback/reference only, explicitly versioned.
5. **Human documentation** — schema/semantic reference only; it must never silently fabricate missing records.

The verified source registry is `data/static/source_registry.json`.

## Snapshot rule

Online data is downloaded during a controlled bootstrap/import step, not continuously inside the gameplay loop. The imported snapshot is stored locally with:

- source identifier and URL;
- retrieval timestamp;
- source/version when available;
- SHA-256 checksum;
- dataset name;
- validation status.

Runtime consumes the validated snapshot. If an online source is unavailable, NosAi may use a previously validated snapshot according to the dataset policy. It must report when data are stale.

## Important constraints

- Never invent an API endpoint merely because a project appears to expose an API.
- Never silently replace current client data with an old community dump.
- Never commit large copyrighted game-data dumps into the NosAi source tree unless licensing/redistribution rights are clear.
- Prefer downloading data to a local runtime/cache directory and keeping only manifests, schemas, provenance and tests in Git.
- Every dataset used by decision-making must be traceable to a source and version/checksum.

## NosTale-specific acquisition strategy

For version-accurate game knowledge, the first practical path is to inspect the user's installed client data. `taletool` can inspect/unpack relevant NosTale containers, including `NSgtdData` and map-related files. Public community sources such as NosData and the NosTale Research Project are used to enrich/validate the extracted snapshot, not to override the current client blindly.

Historical repositories such as `ON.NosWings.Parsing` are allowed only as explicitly labelled legacy fallbacks.

# Repository migration

## Current phase

NosAi is moving from a release-archive repository to a source-first repository while preserving runtime behavior.

### Frozen baseline

- Release: `4.19.2`
- Archive: `NosAi_v4_19.2_FULL_RUNTIME_FUSION.zip`
- Baseline regression suite: 154 passing tests at audit time

### Phase 1: repository foundation

Completed on the migration branch:

- repository ignore rules;
- modern Python project metadata;
- contribution guidance;
- changelog baseline;
- transitional CI that extracts and tests the release archive.

### Phase 2: source-first extraction

The next migration step will extract the verified source tree under `NosAi/`/repository root, remove generated artifacts such as `__pycache__`, and preserve the archive temporarily for reproducibility until source equivalence is verified.

### Safety rule

The release archive must not be deleted until the extracted source tree passes the same regression suite and a source/archive equivalence check has been completed.
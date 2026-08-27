# NosAi Branching and Release Policy

## Purpose

Keep `main` trustworthy while allowing NosAi to evolve continuously without mixing experimental work with the confirmed baseline.

## Branch roles

### `main`

`main` is the confirmed/stable branch. It contains only the latest version explicitly promoted after validation.

Normal development must not happen directly on `main`.

### `develop/nosai-next`

This is the integration branch for the next NosAi candidate. It is the default destination for completed feature/fix work before release validation.

### Feature, fix, pilot, audit and architecture branches

These remain focused working branches. Once work is ready for integration, it should flow into `develop/nosai-next`.

## Candidate lifecycle

```text
feature/fix/pilot
        |
        v
develop/nosai-next
        |
        +--> tests / CI / coverage / diagnostics / Test Center
        |
        +--> runtime and integration validation
        |
        v
release candidate
        |
        +--> explicit confirmation
        |
        v
PR: develop/nosai-next -> main
        |
        v
main = confirmed version
```

## Promotion gate

A candidate must satisfy all applicable checks before it is promoted:

1. Repository builds/install checks pass.
2. Unit and regression tests pass.
3. Integration tests pass where applicable.
4. CI quality/security checks pass.
5. Coverage/reporting checks pass where configured.
6. Test Center validation is green for the affected scope.
7. Runtime/client validation passes for changes that touch the live-client boundary.
8. No unresolved release-blocking defect remains.
9. Version metadata is internally consistent.
10. The candidate is explicitly confirmed for promotion.

A failing or unverified gate means the candidate stays on `develop/nosai-next`.

## Versioning rule

`pyproject.toml` is the package/build source of truth. `version.json` and release-facing documentation must agree with it.

For the current development baseline the canonical version is **4.21.0**.

Any mismatch among these sources is a release blocker and must be fixed before promotion.

## Confirmation rule

The phrase **"conferma questa versione"** is treated as an explicit release confirmation only after the candidate validation results are available. Confirmation authorizes promotion of that validated candidate; it does not waive failed tests or known release blockers.

## Rollback principle

If a promoted version is later found defective, do not rewrite history unnecessarily. Identify the last known-good commit/version, prepare a corrective candidate on `develop/nosai-next`, validate it, and promote the correction through the same gate.

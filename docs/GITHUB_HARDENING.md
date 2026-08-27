# GitHub hardening checklist for NosAi

This repository is configured to keep CI deterministic, auditable, and low-privilege. The remaining controls below are GitHub account/repository settings rather than repository files.

## Recommended repository settings

- Keep `main` as the protected default branch.
- Require pull requests for changes to `main` when collaborative development is enabled.
- Require the relevant CI/security checks before merge.
- Require conversation resolution before merge.
- Disable force-pushes and branch deletion on protected release branches.
- Keep `GITHUB_TOKEN` permissions read-only by default and grant write permission only to jobs that publish evidence/releases.
- Restrict third-party Actions to trusted publishers where practical.
- Keep Actions referenced by immutable commit SHA.
- Enable dependency graph and Dependabot alerts/security updates.
- Enable private vulnerability reporting when available.

## Release controls

Release workflow runs only from version tags (`v*.*.*`) or explicit manual dispatch. Release artifacts are built, smoke-tested, uploaded, and provenance-attested.

## Runtime controls

Windows validation remains a separate gate because the target runtime is Windows while most deterministic CI runs on Linux.

## Test Center controls

The latest Test Center snapshot is persisted under `.nosai/test-center/latest.json`; generated CI evidence is retained as artifacts for forensic review.

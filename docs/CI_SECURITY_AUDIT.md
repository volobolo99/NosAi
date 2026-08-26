# CI + Security Audit

## Scope

Audit of `.github/workflows` on the ZMSIA/NosAi development line, focused on CI completeness, least-privilege permissions, dependency/SAST coverage, action pinning, and separation of optional vendor scanners.

## Current strengths

- `ci.yml` already has top-level `contents: read`, concurrency cancellation, source-tree checks, compilation, pytest regression, and the AI evaluation gate.
- CodeQL is enabled for Python on pull requests, pushes to `main`, and a weekly schedule.
- APIsec and Black Duck workflows are gated behind repository variables rather than failing an unconfigured repository.
- Third-party security actions that are enabled in the existing optional scanners are pinned to commit SHAs.

## Findings

### P1 — Workflow action pinning is inconsistent

Several existing workflows use floating major tags such as `actions/checkout@v4`, `actions/setup-python@v5`, and `github/codeql-action@v3`. These are convenient but are not immutable references. The new `security-ci.yml` intentionally detects this condition so the repository can migrate all workflows to immutable SHAs in a controlled change.

### P1 — Dependency vulnerability and Python SAST were not part of the baseline CI

The baseline CI did not run `pip-audit` or Bandit. `security-ci.yml` adds both as explicit security gates.

### P2 — CI and security gates are separated

Security scanning is kept in its own workflow so a vendor outage does not obscure the deterministic source regression gate. The eventual branch protection policy should require the deterministic CI plus CodeQL/security gates, while optional vendor workflows remain conditional until their credentials and projects are configured.

### P2 — Full workflow hardening still requires repository-level policy

GitHub repository rules should eventually require pull-request reviews, required status checks, and prevention of direct pushes to `main`. Those settings are outside the repository file tree and must be configured as repository rules/branch protection.

## Target gate model

```text
PR
 ├── CI: compile + tests + evaluation
 ├── Security: pip-audit + Bandit
 ├── CodeQL
 └── Workflow security policy
          ↓
      required checks
          ↓
       merge gate
```

## Remediation order

1. Keep the new security audit visible and failing on the currently known action-pinning debt.
2. Pin every GitHub Action to an immutable commit SHA after verifying the exact upstream commit.
3. Re-run security and regression workflows.
4. Add the resulting checks to branch protection/rulesets.
5. Only then make the complete gate mandatory for the ZMSIA integration branches.

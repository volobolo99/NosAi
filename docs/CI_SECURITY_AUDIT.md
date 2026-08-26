# CI + Security Audit

## Scope

Audit of `.github/workflows` on the ZMSIA/NosAI development line, focused on CI completeness, least-privilege permissions, dependency/SAST coverage, action pinning, and separation of optional vendor scanners.

## Current strengths

- `ci.yml` has explicit read-only repository permissions, concurrency cancellation, source-tree checks, compilation, pytest regression, and the AI evaluation gate.
- CodeQL is enabled for Python on pull requests, pushes to `main`, and a weekly schedule.
- APIsec and Black Duck are gated behind repository variables rather than failing an unconfigured repository.
- Third-party security actions are pinned to commit SHAs.
- Core GitHub-maintained actions used by this project are now pinned to immutable commit SHAs.
- `security-ci.yml` runs dependency auditing with `pip-audit`, Python SAST with Bandit, and a repository-wide workflow policy check.

## Findings and remediation

### P1 — Workflow action pinning

**Resolved on this branch.** The previous floating major tags (`checkout@v4`, `setup-python@v5`, `codeql-action@v3`, `upload-artifact@v4`, and `sonarqube-scan-action@v6`) were replaced with verified commit SHAs. The workflow policy now requires every `uses:` reference to contain a full 40-character commit SHA.

The CodeQL v3 reference was resolved to its current tag commit before pinning; the SonarCloud v6 tag resolves directly to a commit. The pinned checkout/setup-python releases are verified GitHub releases. 

### P1 — Dependency vulnerability and Python SAST

**Implemented.** `security-ci.yml` adds `pip-audit` and Bandit as explicit security gates.

### P2 — CI and security separation

Security scanning remains separate from deterministic source regression so an optional vendor outage does not obscure the core regression gate. APIsec/Black Duck remain conditional until their repository credentials/projects are configured.

### P2 — Repository-level merge policy

Still required outside the file tree: protect `main`, require pull requests, require the deterministic CI/security/CodeQL checks, and prevent direct pushes. This should be configured only after the branch has passed its first full Actions run.

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

## Remediation status

1. Security audit workflow — **done**.
2. Dependency/SAST gates — **done**.
3. Immutable action pinning — **done**.
4. Full Actions execution — **next gate**.
5. Repository branch protection/rulesets — **after successful full run**.
6. ZMSIA runtime Safety/Evaluation gates — **after CI baseline is green**.

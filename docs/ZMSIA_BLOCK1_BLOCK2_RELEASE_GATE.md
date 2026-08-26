# ZMSIA Blocks 1 + 2 release gate

This branch intentionally combines the Core Foundation and Quality/Security gate work to reduce integration churn.

## Block 1 — Core Foundation

- provider-neutral contracts
- M1/M2 adapters
- deterministic Mock provider
- orchestrator
- validation
- deny-by-default safety policy
- deterministic evaluation gate
- append-only dry-run telemetry
- end-to-end safe/evaluated cycle tests

## Block 2 — Quality + Security

- Ruff across `app` and `tests`
- compileall
- full pytest regression suite
- AI evaluation gate
- pip-audit
- Bandit SAST
- CodeQL with immutable action pins
- workflow permission + SHA audit
- hardware benchmark action pinning
- optional third-party scanners kept configuration-gated

## Release rule

No Local AI, OpenAI provider, executor, or live client integration should be enabled until this combined PR is green across the required CI/security checks.

After green: start Block 3 as one hybrid-AI integration slice (Local + OpenAI behind the same DecisionProvider contract, shadow/A-B evaluation, no live execution).

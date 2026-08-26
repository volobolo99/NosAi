# NosAi diagnostics contract

NosAi must diagnose itself before entering a runtime mode.

## Startup

`run_startup_checks()` validates importable core components and accepts extra deterministic checks. It never connects to the live game and never executes OS input.

## Support bundle

`write_support_bundle(report, path)` writes `nosai-support-bundle-v1` JSON. Secret-like keys are redacted before writing.

## Planned checks

The diagnostics layer is intentionally extensible. The next checks should cover:

1. Python/runtime compatibility.
2. Package/dependency versions.
3. repository/config schema validity.
4. fixture/replay integrity.
5. decoder coverage and unknown-packet ratio.
6. GameState invariants.
7. benchmark regression thresholds.
8. capture adapter readiness (without enabling capture).
9. model/provider configuration, with credentials never reported.
10. disk/write permissions for replay and diagnostics output.

A failed critical check must block autonomous modes; warnings may allow Observe/Shadow only.

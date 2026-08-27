# NosAi Gate — End-to-End Verification

## Scope

Verify the progression path from a read-only World State through CharacterSnapshot, PlayAi proposal, GuardAi evaluation and the control/safety boundary.

## Verified by repository-level integration fixture

`tests/test_progression_end_to_end.py` exercises:

`WorldState fixture -> CharacterSnapshot -> PlayAiGuardAiBridge -> GuardAi evaluation -> non-authorized execution result`.

The bridge explicitly returns `execution_authorized=False` and the test asserts this invariant.

## Static integration checks

- CharacterSnapshot contract matches the adapter fields.
- PlayAiGuardAiBridge imports the repository's `ProgressionAdvisor`.
- Decision gate maps blocked recommendations to `RunState.BLOCKED` and otherwise leaves the run in `RunState.EVALUATING` without execution authorization.
- Control-plane lifecycle does not permit arbitrary state skipping.

## Not yet proven by this gate

A real running NosTale process has not been attached to the normalized World State adapter in this environment. Therefore this gate is **repository/integration-fixture verified**, not live-runtime verified.

The next evidence gate must run the actual runtime adapter, then execute the complete CI/Test Center suite and record the workflow result.

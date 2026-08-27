## NosAi release / change checklist

### Change type
- [ ] Feature
- [ ] Fix
- [ ] Refactor
- [ ] Test/CI
- [ ] Release promotion (`develop/nosai-next` -> `main`)

### Validation
- [ ] Unit/regression tests pass
- [ ] Integration tests pass where applicable
- [ ] CI quality/security gates pass
- [ ] Coverage/reporting checks pass where configured
- [ ] Test Center checks pass for the affected scope
- [ ] Runtime/client validation completed when applicable
- [ ] No known release-blocking defect remains
- [ ] Version metadata is consistent

### Promotion gate
For a PR targeting `main`:

- [ ] This candidate was validated on `develop/nosai-next`.
- [ ] The candidate was explicitly confirmed for promotion.
- [ ] The PR is the intended promotion of the confirmed candidate.

Do not use a PR to `main` to bypass validation on `develop/nosai-next`.

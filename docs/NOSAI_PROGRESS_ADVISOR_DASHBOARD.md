# NosAi — Progression Advisor Dashboard

## Main dashboard panel

Add a first-class **GuardAi Progression Advisor** panel to the main control dashboard.

### User view

1. Current objective
2. Character health/progression snapshot
3. Detected bottleneck
4. Top three candidate plans
5. Quantitative simulation comparison
6. Recommended plan and confidence
7. Reasons and evidence
8. Policy/risk status
9. Estimated time/resources to target
10. Recalculate button and last-update timestamp

## Comparison card

Each candidate shows:

- expected progress;
- probability of success;
- expected time-to-target;
- resource/cost requirement;
- risk score;
- confidence/data quality;
- simulation count/version;
- policy status.

Use ranges and confidence bands whenever uncertainty is material.

## Recommendation states

- RECOMMENDED
- CONDITIONAL
- LOW_VALUE
- NOT_RECOMMENDED
- BLOCKED_BY_POLICY
- INSUFFICIENT_DATA

A blocked/invalid plan must not expose an execution action.

## Interaction model

PlayAi proposes candidate goals/strategies from the current state. GuardAi independently evaluates them and can generate alternatives. Decision Fabric arbitrates. Dashboard renders the result and asks for human approval where required.

## Refresh triggers

Recompute on meaningful changes to:

- character snapshot;
- equipment/resources;
- target objective;
- relevant game rules/version;
- market observations;
- simulator version;
- cloud benchmark availability.

## Explainability

Every recommendation should expose a compact explanation plus expandable evidence: inputs, assumptions, simulator version, seed/batch, data provenance and main factors affecting the result.

## Safety

The dashboard is advisory/control UI. It must not provide automatic purchase/payment/trade execution for prohibited RMT activity, and no cloud result can directly authorize game execution.

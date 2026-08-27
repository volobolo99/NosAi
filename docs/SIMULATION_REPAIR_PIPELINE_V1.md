# NosAi Simulation & Repair Research Pipeline V1

## Objective

When a real or CI test records a concrete failure, NosAi may investigate it automatically in an isolated, non-production environment. The system researches candidate explanations and candidate fixes, evaluates them through deterministic simulation, and produces evidence for human review.

The pipeline is an engineering aid, not an autonomous production-code writer.

## Lifecycle

```text
TEST FAILURE
    |
    v
NORMALIZE ERROR
    |
    +--> fingerprint / deduplicate
    |
    +--> collect exact evidence
    |
    v
RESEARCH
    |
    +--> official documentation
    +--> upstream repositories/issues
    +--> GitHub code/issues/PRs
    +--> trusted technical sources
    |
    v
CANDIDATE SET
    |
    +--> explanation candidates
    +--> patch candidates
    +--> dependency/configuration candidates
    |
    v
ISOLATED SIMULATION
    |
    +--> clean workspace
    +--> pinned dependencies
    +--> no production credentials
    +--> no write access to main
    |
    v
VERIFY CANDIDATES
    |
    +--> syntax/import
    +--> unit/regression
    +--> targeted reproduction
    +--> property/fuzz cases where applicable
    +--> static analysis
    +--> deterministic replay
    |
    v
CANDIDATE REPORT
    |
    +--> pass/fail evidence
    +--> reproducibility
    +--> provenance
    +--> confidence metadata
    |
    v
HUMAN REVIEW
    |
    v
OPTIONAL IMPLEMENTATION
    |
    v
FULL TEST SUITE
    |
    v
REAL HOST RETEST (when applicable)
```

## Research policy

Research results are evidence, not authority. Sources are ranked by provenance: official documentation and upstream project sources first, then maintained repositories/issues, then reputable technical references. Search snippets alone are never treated as proof.

External code is not copied automatically. A candidate must pass license/provenance checks, security review, API compatibility checks, and the NosAi test suite before it can be considered.

## Candidate isolation

Every candidate runs in a disposable workspace or equivalent isolated environment. Candidate execution must not modify `main`, the user's live installation, secrets, or the real NosTale session. Network access is denied by default for simulation execution and is enabled only for an explicit research phase.

## No automatic production promotion

Even if a candidate passes simulation, it remains a candidate. Passing simulation means only that the candidate satisfies the defined simulated evidence. A real Windows/NosTale failure requires a real-host retest before the change can be treated as validated for that environment.

## Dashboard telemetry

The dashboard exposes only progress and evidence summaries:

- research state;
- number of sources considered;
- candidate count;
- current simulation stage;
- candidate pass/fail counts;
- elapsed time;
- current run ID;
- artifact/report IDs.

It does not expose raw research or patch content unless explicitly requested through the report/artifact view.

## Failure states

- `REPORTED`: original failure recorded;
- `RESEARCHING`: sources being collected;
- `CANDIDATES_READY`: candidate set created;
- `SIMULATING`: isolated execution in progress;
- `VALIDATED_IN_SIMULATION`: candidate passed the configured simulation gates;
- `SIMULATION_FAILED`: no candidate passed or the simulation itself failed;
- `READY_FOR_REVIEW`: evidence package is complete;
- `REAL_RETEST_REQUIRED`: real-host verification is required;
- `PROMOTED`: only after normal NosAi release gates and explicit confirmation.

## Security boundaries

The research/simulation system must sanitize secrets, tokens, cookies, account identifiers, local credentials, and personal data before sending error context to external research services. It must never upload a raw process memory dump or unrelated private files. Only the minimum error context needed for research is transmitted.

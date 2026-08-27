# NosAi External Research & Reuse Policy V1

## Research sources

For programming and debugging work, research should prioritize:

1. official language/platform documentation;
2. upstream project documentation and source repositories;
3. GitHub issues, pull requests and maintained implementations;
4. reputable technical references;
5. community discussions only as supporting evidence.

For Windows runtime work, Microsoft documentation and Windows-native diagnostics are preferred. For observability, OpenTelemetry concepts are preferred. For Python testing, established pytest/Hypothesis patterns are preferred. For static analysis, established tools such as Pyright and Semgrep are preferred when their findings are useful to the project.

## Reuse decision

Before incorporating an external implementation, record:

- project/repository;
- exact version or commit;
- license;
- relevant component;
- reason for reuse;
- compatibility assessment;
- security assessment;
- whether a dependency or a clean reimplementation is preferable.

Do not copy large portions of a project when a small dependency, documented algorithm, or clean original implementation is sufficient.

## Research-to-simulation boundary

Online research may produce hypotheses and candidate implementations. It must never be treated as proof that a candidate works in NosAi. Every candidate must be replayed against the original failure in isolation and then through the appropriate real/CI test layer.

## Source traceability

Each researched candidate receives a source manifest and a stable candidate ID. The final report links the candidate to its research sources, simulation evidence, test results, and any later real-host retest.

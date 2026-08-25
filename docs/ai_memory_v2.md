
# AI Memory v2

AI Memory v2 adds five layers:

1. Working Memory
2. Episodic Observations
3. Consolidated Facts
4. Candidate Inferences
5. Strategy Experience / Learning

Flow:

OBSERVATION
    -> WORKING MEMORY
    -> CONSOLIDATION
    -> FACT / INFERENCE
    -> RETRIEVAL
    -> STRATEGY CONTEXT

Important design rule:
observations are preserved as source evidence; inferred knowledge is explicitly
marked as an inference and is not silently promoted to fact.

Strategy learning stores outcomes such as success, reward, duration and risk.
The StrategyEngine can use these rankings as an additional scoring signal.

The reference implementation uses an in-memory store so it is deterministic
and easy to test. A production adapter can persist the same models in SQLite
or another approved datastore without changing the higher-level interfaces.

from app.ai.contracts import ActionIntent, ActionKind, Goal, MemoryRecord, Outcome, RewardEvidence
from app.memory import EpisodicMemory, MemoryQuery


def record(fp: str, goal: str = "survive") -> MemoryRecord:
    return MemoryRecord(
        state_fingerprint=fp,
        goal=Goal(kind=goal),
        intent=ActionIntent(ActionKind.NOOP),
        outcome=Outcome(status="success"),
        reward=RewardEvidence(components={"survival": 1.0}),
    )


def test_memory_is_bounded_and_keeps_recent_records():
    memory = EpisodicMemory(capacity=2)
    memory.extend([record("a"), record("b"), record("c")])
    assert len(memory) == 2
    assert [r.state_fingerprint for r in memory.recent(10)] == ["c", "b"]


def test_memory_query_filters_state_and_goal():
    memory = EpisodicMemory()
    memory.extend([record("a", "survive"), record("a", "kill"), record("b", "survive")])
    result = memory.query(MemoryQuery(state_fingerprint="a", goal_kind="survive"))
    assert len(result) == 1
    assert result[0].state_fingerprint == "a"


def test_memory_rejects_invalid_records_and_capacity():
    memory = EpisodicMemory(capacity=1)
    try:
        memory.append(object())
    except TypeError:
        pass
    else:
        raise AssertionError("invalid memory record accepted")

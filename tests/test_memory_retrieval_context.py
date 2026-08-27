from app.ai.contracts import ActionIntent, ActionKind, Goal, MemoryRecord, Outcome, RewardEvidence
from app.memory import ContextBuilder, MemoryRetriever


def _record(state: str, goal: str, action: ActionKind, reward: float = 0.0) -> MemoryRecord:
    return MemoryRecord(
        state_fingerprint=state,
        goal=Goal(kind=goal),
        intent=ActionIntent(kind=action),
        outcome=Outcome(status="ok"),
        reward=RewardEvidence(components={"total": reward}),
    )


def test_retrieval_is_deterministic_and_bounded() -> None:
    records = [
        _record("s1", "farm", ActionKind.ATTACK, 10),
        _record("s2", "farm", ActionKind.MOVE, 20),
        _record("s1", "farm", ActionKind.MOVE, -10),
    ]
    retriever = MemoryRetriever(max_results=2)
    first = retriever.retrieve(records, state_fingerprint="s1", goal_kind="farm")
    second = retriever.retrieve(records, state_fingerprint="s1", goal_kind="farm")
    assert first == second
    assert len(first) == 2
    assert first[0].record.state_fingerprint == "s1"


def test_context_builder_is_bounded_and_explainable() -> None:
    records = [_record("s1", "farm", ActionKind.ATTACK, 10)]
    matches = MemoryRetriever().retrieve(records, state_fingerprint="s1", goal_kind="farm")
    context = ContextBuilder(max_items=1, max_chars=500).build(matches)
    assert len(context.items) == 1
    assert "same_state" in context.text
    assert "score=" in context.text


def test_context_builder_respects_character_limit() -> None:
    records = [_record(f"state-{i}", "farm", ActionKind.ATTACK, 10) for i in range(5)]
    matches = MemoryRetriever(max_results=5).retrieve(records, goal_kind="farm")
    context = ContextBuilder(max_items=5, max_chars=100).build(matches)
    assert len(context.text) <= 100

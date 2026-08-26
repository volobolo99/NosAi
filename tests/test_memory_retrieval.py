from app.ai.contracts import ActionIntent, ActionKind, Goal, MemoryRecord, Outcome, RewardEvidence
from app.memory.retrieval import MemoryRetriever


def make_record(fp, goal, action, reward):
    return MemoryRecord(fp, Goal(goal), ActionIntent(ActionKind(action)), Outcome("success"), RewardEvidence({"total": reward}))


def test_retriever_prefers_matching_state_and_goal():
    records = [make_record("other", "progress", "wait", 100), make_record("same", "survive", "retreat", 20)]
    matches = MemoryRetriever().retrieve(records, state_fingerprint="same", goal_kind="survive")
    assert matches[0].record.state_fingerprint == "same"
    assert "same_state" in matches[0].reasons
    assert "same_goal" in matches[0].reasons


def test_retriever_is_bounded_and_deterministic():
    records = [make_record(str(i), "progress", "wait", i) for i in range(10)]
    first = MemoryRetriever(max_results=3).retrieve(records, goal_kind="progress")
    second = MemoryRetriever(max_results=3).retrieve(records, goal_kind="progress")
    assert len(first) == 3
    assert [m.record.state_fingerprint for m in first] == [m.record.state_fingerprint for m in second]

from app.ai.contracts import ActionKind
from app.memory.learning_memory_bridge import LearningMemoryBridge


class FakeMemory:
    def __init__(self):
        self.records = []

    def add(self, record):
        self.records.append(record)


def test_bridge_records_transition_without_executing_action():
    memory = FakeMemory()
    bridge = LearningMemoryBridge(memory)
    record = bridge.record_transition({"hp": 0.5}, "attack", {"hp": 0.4}, 1.25, False)

    assert len(memory.records) == 1
    assert record.intent.kind is ActionKind.ATTACK
    assert record.reward.components["total"] == 1.25
    assert record.outcome.status == "ongoing"

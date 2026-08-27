from nosai.local_ai.protocol import AIMessage, MessageType
from nosai.local_ai.shared_memory import SharedMemory

def test_protocol_message_is_versioned_and_validated():
    message = AIMessage.create(sender="primary", recipient="secondary", type=MessageType.TASK, payload={"task": "combat"}, context_id="state-1")
    message.validate()
    assert message.protocol_version == "1.0"

def test_shared_memory_versions_authorized_updates():
    memory = SharedMemory()
    first = memory.write("target", "mob-a", source="primary", confidence=0.9)
    second = memory.write("target", "mob-b", source="secondary", confidence=0.8)
    assert first.version == 1
    assert second.version == 2
    assert memory.read("target").value == "mob-b"

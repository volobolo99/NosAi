from app.ai.brain import BrainObservation, EpisodicMemory, NosAiBrain
from app.ai.replay_buffer import ReplayBuffer, Transition


def test_brain_prioritizes_survival_at_low_hp():
    brain = NosAiBrain()
    decision = brain.decide(BrainObservation({"hp_ratio": 0.1, "objective": "kill_all"}))
    assert decision.action_type in {"heal", "retreat"}
    assert decision.confidence > 0.0


def test_brain_reacts_to_100_percent_resistance():
    brain = NosAiBrain()
    decision = brain.decide(BrainObservation({"hp_ratio": 1.0, "target_resistance": 1.0}))
    assert decision.action_type == "move"
    assert any("100%" in reason for reason in decision.reasons)


def test_memory_influences_similar_states():
    memory = EpisodicMemory()
    memory.remember({"hp_ratio": 0.8, "target_distance": 5}, "attack", 10, "success")
    hits = memory.similar(BrainObservation({"hp_ratio": 0.8, "target_distance": 5}))
    assert hits and hits[0]["action"] == "attack"


def test_replay_buffer_round_trip(tmp_path):
    buffer = ReplayBuffer(capacity=4)
    buffer.add(Transition({"hp": 1}, "attack", 1.0, {"hp": 0.9}))
    path = tmp_path / "replay.jsonl"
    buffer.save_jsonl(path)

    restored = ReplayBuffer(capacity=4)
    assert restored.load_jsonl(path) == 1
    assert len(restored) == 1
    assert restored.recent()[0].action == "attack"

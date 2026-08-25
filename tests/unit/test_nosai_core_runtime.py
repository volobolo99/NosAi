from app.nosai_runtime import NosAiCoreRuntime
from app.world_model.actions import WorldAction


def test_core_runtime_traverses_all_modules_and_uses_learned_world_model():
    rt = NosAiCoreRuntime(memory_path=":memory:", seed=7)
    actions = [
        WorldAction("ATTACK", "ATTACK", {"target_id": "mob:1", "damage": 10}),
        WorldAction("MOVE", "MOVE", {"position": (1, 0)}),
    ]
    result = rt.decide(rt.bootstrap_state, actions)
    assert result.world_model_trained
    assert result.action.action_id in {"ATTACK", "MOVE"}
    assert result.trace == tuple(f"M{i}" for i in range(1, 16))
    assert rt.steps == 1
    rt.close()


def test_core_runtime_persists_memory_records():
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "memory.db"
        rt = NosAiCoreRuntime(memory_path=path)
        action = WorldAction("ATTACK", "ATTACK", {"target_id": "mob:1", "damage": 10})
        rt.decide(rt.bootstrap_state, [action])
        rt.close()
        import sqlite3
        db = sqlite3.connect(path)
        assert db.execute("select count(*) from observations").fetchone()[0] >= 2
        db.close()


def test_core_runtime_reloads_persistent_memory_after_restart():
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "memory.db"
        action = WorldAction("ATTACK", "ATTACK", {"target_id": "mob:1", "damage": 10})
        rt = NosAiCoreRuntime(memory_path=path, seed=5)
        rt.decide(rt.bootstrap_state, [action])
        rt.close()
        rt2 = NosAiCoreRuntime(memory_path=path, seed=5)
        assert len(rt2.memory_store.observations) >= 2
        rt2.close()

from app.integrations.replay import append_observation, iter_observations


def test_replay_round_trip(tmp_path):
    path = tmp_path / "episode.jsonl"
    append_observation(path, {"sequence": 1, "player": {"x": 2}})
    append_observation(path, {"sequence": 2, "player": {"x": 3}})
    assert list(iter_observations(path)) == [
        {"player": {"x": 2}, "sequence": 1},
        {"player": {"x": 3}, "sequence": 2},
    ]

from __future__ import annotations

from pathlib import Path

from app.nostale_perception.perception import Frame
from app.nostale_perception.replay import ReplayFrameSource, write_jsonl


def test_replay_round_trip_preserves_frame_and_hash(tmp_path: Path) -> None:
    frames = [
        Frame("f1", 1000, 2, 1, b"abcd", "test"),
        Frame("f2", 1016, 2, 1, b"efgh", "test"),
    ]
    path = tmp_path / "frames.jsonl"
    write_jsonl(path, frames)

    replay = ReplayFrameSource.load_jsonl(path)
    first = replay.capture()
    second = replay.capture()

    assert first == frames[0]
    assert second == frames[1]
    assert first.sha256 == frames[0].sha256
    assert second.sha256 == frames[1].sha256

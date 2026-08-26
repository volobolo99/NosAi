from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.nostale_perception.capture_dataset import append_ground_truth, capture_frames
from app.nostale_perception.ground_truth import FrameGroundTruth
from app.nostale_perception.perception import Frame


class FakeSource:
    def __init__(self) -> None:
        self.index = 0

    def capture(self) -> Frame:
        self.index += 1
        return Frame(f"f{self.index}", self.index, 1, 1, b"abcd", "test")


def test_capture_frames_writes_bounded_replay_records(tmp_path: Path) -> None:
    path = tmp_path / "frames.jsonl"
    assert capture_frames(FakeSource(), path, 3) == 3
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    assert json.loads(lines[2])["frame_id"] == "f3"


def test_ground_truth_append_rejects_duplicate(tmp_path: Path) -> None:
    path = tmp_path / "truth.jsonl"
    truth = FrameGroundTruth("f1", hp=10)
    append_ground_truth(path, truth)
    with pytest.raises(ValueError, match="duplicate"):
        append_ground_truth(path, truth)

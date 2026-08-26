from __future__ import annotations

from pathlib import Path

import pytest

from app.nostale_perception.ground_truth import load_ground_truth


def test_ground_truth_is_unique_and_typed(tmp_path: Path) -> None:
    path = tmp_path / "truth.jsonl"
    path.write_text('{"frame_id":"f1","hp":950,"hp_max":1000,"map_name":"NosVille"}\n', encoding="utf-8")
    truth = load_ground_truth(path)
    assert truth["f1"].hp == 950
    assert truth["f1"].map_name == "NosVille"


def test_duplicate_ground_truth_frame_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "truth.jsonl"
    path.write_text('{"frame_id":"f1"}\n{"frame_id":"f1"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_ground_truth(path)

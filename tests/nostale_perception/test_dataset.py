from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.nostale_perception.dataset import build_manifest, sha256_file, write_manifest


def test_dataset_manifest_is_content_addressed(tmp_path: Path) -> None:
    frames = tmp_path / "frames.jsonl"
    truth = tmp_path / "ground_truth.jsonl"
    manifest_path = tmp_path / "manifest.json"
    frames.write_text('{"frame_id":"f1","timestamp_ms":1,"width":1,"height":1,"pixels_hex":"00000000","source":"test"}\n', encoding="utf-8")
    truth.write_text('{"frame_id":"f1","hp":10}\n', encoding="utf-8")

    manifest = build_manifest("nostale-calibration", "0.1.0", frames, truth)
    write_manifest(manifest_path, manifest)
    loaded = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest.frame_count == 1
    assert manifest.ground_truth_count == 1
    assert manifest.frames_sha256 == sha256_file(frames)
    assert loaded["ground_truth_sha256"] == sha256_file(truth)


def test_dataset_manifest_rejects_duplicate_frame_ids(tmp_path: Path) -> None:
    frames = tmp_path / "frames.jsonl"
    truth = tmp_path / "ground_truth.jsonl"
    frames.write_text(
        '\n'.join([
            '{"frame_id":"f1","timestamp_ms":1,"width":1,"height":1,"pixels_hex":"00","source":"test"}',
            '{"frame_id":"f1","timestamp_ms":2,"width":1,"height":1,"pixels_hex":"00","source":"test"}',
        ]) + '\n', encoding="utf-8")
    truth.write_text('{"frame_id":"f1"}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        build_manifest("test", "0.1.0", frames, truth)

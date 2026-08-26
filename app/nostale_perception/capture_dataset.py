"""Read-only dataset capture and annotation helpers for Windows replay fixtures."""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .ground_truth import FrameGroundTruth
from .perception import Frame
from .replay import ReplayFrame, write_jsonl


def append_capture(path: str | Path, frame: Frame) -> None:
    """Append one captured frame as a deterministic replay record."""
    record = asdict(ReplayFrame.from_frame(frame))
    with Path(path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def append_ground_truth(path: str | Path, truth: FrameGroundTruth) -> None:
    """Append one annotation; duplicate frame IDs are rejected."""
    target = Path(path)
    if target.exists():
        for line in target.read_text(encoding="utf-8").splitlines():
            if line.strip() and json.loads(line)["frame_id"] == truth.frame_id:
                raise ValueError(f"duplicate ground-truth frame_id: {truth.frame_id}")
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(truth), sort_keys=True) + "\n")


def capture_frames(source, output: str | Path, count: int) -> int:
    """Capture a bounded number of frames; returns the number written."""
    if count <= 0:
        raise ValueError("count must be positive")
    written = 0
    for _ in range(count):
        append_capture(output, source.capture())
        written += 1
    return written

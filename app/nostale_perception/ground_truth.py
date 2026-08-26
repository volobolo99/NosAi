"""Human/fixture-authored ground truth for perception evaluation."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class FrameGroundTruth:
    frame_id: str
    hp: int | None = None
    hp_max: int | None = None
    mp: int | None = None
    mp_max: int | None = None
    player_x: float | None = None
    player_y: float | None = None
    map_name: str | None = None


def load_ground_truth(path: str | Path) -> dict[str, FrameGroundTruth]:
    records: dict[str, FrameGroundTruth] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        record = FrameGroundTruth(**data)
        if record.frame_id in records:
            raise ValueError(f"duplicate ground-truth frame_id: {record.frame_id}")
        records[record.frame_id] = record
    return records

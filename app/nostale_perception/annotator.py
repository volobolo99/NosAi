"""Small, dependency-free terminal annotator for replay ground truth."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .ground_truth import FrameGroundTruth
from .replay import ReplayFrameSource
from .capture_dataset import append_ground_truth


@dataclass(frozen=True)
class AnnotationPrompt:
    frame_id: str
    index: int
    total: int


def annotate_replay(frames_file: str | Path, truth_file: str | Path, input_fn=input, output_fn=print) -> int:
    """Interactively annotate replay frames using conservative optional fields."""
    frames = list(ReplayFrameSource.load_jsonl(frames_file))
    count = 0
    for index, frame in enumerate(frames, 1):
        output_fn(f"[{index}/{len(frames)}] frame={frame.frame_id} {frame.width}x{frame.height}")
        def optional_int(label: str) -> int | None:
            raw = input_fn(f"{label} (blank=unknown): ").strip()
            return None if not raw else int(raw)
        def optional_float(label: str) -> float | None:
            raw = input_fn(f"{label} (blank=unknown): ").strip()
            return None if not raw else float(raw)
        hp = optional_int("HP")
        hp_max = optional_int("HP max")
        mp = optional_int("MP")
        mp_max = optional_int("MP max")
        x = optional_float("Player X")
        y = optional_float("Player Y")
        map_name = input_fn("Map (blank=unknown): ").strip() or None
        append_ground_truth(
            truth_file,
            FrameGroundTruth(frame.frame_id, hp, hp_max, mp, mp_max, x, y, map_name),
        )
        count += 1
    return count

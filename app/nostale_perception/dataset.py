"""Versioned replay/ground-truth dataset manifest primitives."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .ground_truth import FrameGroundTruth, load_ground_truth


@dataclass(frozen=True)
class DatasetManifest:
    name: str
    version: str
    frames_file: str
    ground_truth_file: str
    frame_count: int
    ground_truth_count: int
    frames_sha256: str
    ground_truth_sha256: str


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    name: str,
    version: str,
    frames_file: str | Path,
    ground_truth_file: str | Path,
) -> DatasetManifest:
    truth = load_ground_truth(ground_truth_file)
    frame_lines = [line for line in Path(frames_file).read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(frame_lines) != len(set(json.loads(line)["frame_id"] for line in frame_lines)):
        raise ValueError("duplicate frame_id in replay dataset")
    return DatasetManifest(
        name=name,
        version=version,
        frames_file=str(frames_file),
        ground_truth_file=str(ground_truth_file),
        frame_count=len(frame_lines),
        ground_truth_count=len(truth),
        frames_sha256=sha256_file(frames_file),
        ground_truth_sha256=sha256_file(ground_truth_file),
    )


def write_manifest(path: str | Path, manifest: DatasetManifest) -> None:
    Path(path).write_text(json.dumps(manifest.__dict__, indent=2, sort_keys=True) + "\n", encoding="utf-8")

"""One-command Windows capture session orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .capture_dataset import capture_frames
from .dataset import build_manifest, write_manifest
from .window_discovery import discover_windows
from .windows_backend import Win32WindowCaptureBackend
from .windows_capture import WindowsFrameSource, WindowsWindowTarget


@dataclass(frozen=True)
class CaptureSessionResult:
    hwnd: int
    frames_file: Path
    manifest_file: Path
    frame_count: int


def capture_session(title: str, output_dir: str | Path, count: int, hwnd: int | None = None) -> CaptureSessionResult:
    if count <= 0:
        raise ValueError("count must be positive")
    if hwnd is None:
        candidates = discover_windows(title)
        if len(candidates) != 1:
            raise RuntimeError(f"expected exactly one matching window, found {len(candidates)}")
        candidate = candidates[0]
        target = WindowsWindowTarget(candidate.hwnd, candidate.pid, candidate.title)
    else:
        target = WindowsWindowTarget(hwnd)

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    frames_file = output / "frames.jsonl"
    truth_file = output / "ground_truth.jsonl"
    manifest_file = output / "manifest.json"

    source = WindowsFrameSource(target, Win32WindowCaptureBackend())
    written = capture_frames(source, frames_file, count)
    if not truth_file.exists():
        truth_file.write_text("", encoding="utf-8")
    manifest = build_manifest("nostale-real-capture", "0.1.0", frames_file, truth_file)
    write_manifest(manifest_file, manifest)
    return CaptureSessionResult(target.hwnd, frames_file, manifest_file, written)

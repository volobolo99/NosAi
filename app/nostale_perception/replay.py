"""Deterministic frame replay primitives for NosTale perception tests."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterator

from .perception import Frame, FrameSource


@dataclass(frozen=True)
class ReplayFrame:
    frame_id: str
    timestamp_ms: int
    width: int
    height: int
    pixels_hex: str
    source: str = "replay"

    @classmethod
    def from_frame(cls, frame: Frame) -> "ReplayFrame":
        return cls(
            frame_id=frame.frame_id,
            timestamp_ms=frame.timestamp_ms,
            width=frame.width,
            height=frame.height,
            pixels_hex=(frame.pixels or b"").hex(),
            source=frame.source,
        )

    def to_frame(self) -> Frame:
        return Frame(
            frame_id=self.frame_id,
            timestamp_ms=self.timestamp_ms,
            width=self.width,
            height=self.height,
            pixels=bytes.fromhex(self.pixels_hex),
            source=self.source,
        )


class ReplayFrameSource(FrameSource):
    """Replay a finite immutable sequence in capture order."""

    def __init__(self, frames: list[ReplayFrame]) -> None:
        self._frames = tuple(frames)
        self._index = 0

    @classmethod
    def load_jsonl(cls, path: str | Path) -> "ReplayFrameSource":
        frames: list[ReplayFrame] = []
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                frames.append(cls._decode(line))
        return cls(frames)

    @staticmethod
    def _decode(line: str) -> ReplayFrame:
        data = json.loads(line)
        return ReplayFrame(**data)

    def capture(self) -> Frame:
        if self._index >= len(self._frames):
            raise StopIteration("replay exhausted")
        frame = self._frames[self._index].to_frame()
        self._index += 1
        return frame

    def __iter__(self) -> Iterator[Frame]:
        while self._index < len(self._frames):
            yield self.capture()


def write_jsonl(path: str | Path, frames: list[Frame]) -> None:
    """Persist frames as deterministic JSONL metadata plus hexadecimal pixels."""
    lines = [json.dumps(ReplayFrame.from_frame(frame).__dict__, sort_keys=True) for frame in frames]
    Path(path).write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

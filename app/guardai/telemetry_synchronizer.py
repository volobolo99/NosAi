from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Mapping


@dataclass(slots=True)
class FrameTelemetryPair:
    """A video frame correlated with the closest telemetry sample by PTS."""

    frame_id: int
    video_pts_us: int
    telemetry_pts_us: int
    telemetry_payload: dict[str, Any]
    skew_us: int


class GuardAiTelemetrySynchronizer:
    """Bounded PTS-based synchronizer for GuardAi video and telemetry streams.

    Telemetry is kept in a bounded time-ordered buffer. Matching is deterministic:
    among samples inside ``tolerance_us``, the closest PTS wins and ties prefer the
    older sample. Stale telemetry is never paired with a frame.
    """

    def __init__(self, *, tolerance_us: int = 5_000, max_buffer_size: int = 256) -> None:
        if tolerance_us < 0:
            raise ValueError("tolerance_us must be non-negative")
        if max_buffer_size <= 0:
            raise ValueError("max_buffer_size must be positive")
        self.tolerance_us = tolerance_us
        self.max_buffer_size = max_buffer_size
        self._telemetry: Deque[tuple[int, dict[str, Any]]] = deque()

    def add_telemetry(self, pts_us: int, payload: Mapping[str, Any]) -> None:
        """Add a telemetry sample while preserving PTS order and bounded memory."""
        if pts_us < 0:
            raise ValueError("pts_us must be non-negative")
        item = (pts_us, dict(payload))
        if not self._telemetry or pts_us >= self._telemetry[-1][0]:
            self._telemetry.append(item)
        else:
            items = list(self._telemetry)
            index = next(i for i, (existing_pts, _) in enumerate(items) if pts_us < existing_pts)
            items.insert(index, item)
            self._telemetry = deque(items)
        while len(self._telemetry) > self.max_buffer_size:
            self._telemetry.popleft()

    def pair_frame(self, frame_id: int, video_pts_us: int) -> FrameTelemetryPair | None:
        """Return the closest telemetry sample within tolerance, if available."""
        if frame_id < 0 or video_pts_us < 0:
            raise ValueError("frame_id and video_pts_us must be non-negative")
        if not self._telemetry:
            return None

        best_index: int | None = None
        best_key: tuple[int, int] | None = None
        for index, (telemetry_pts, _) in enumerate(self._telemetry):
            skew = abs(video_pts_us - telemetry_pts)
            if skew <= self.tolerance_us:
                key = (skew, telemetry_pts)
                if best_key is None or key < best_key:
                    best_index, best_key = index, key

        if best_index is None:
            self._drop_stale(video_pts_us)
            return None

        telemetry_pts, payload = self._telemetry[best_index]
        del self._telemetry[best_index]
        return FrameTelemetryPair(
            frame_id=frame_id,
            video_pts_us=video_pts_us,
            telemetry_pts_us=telemetry_pts,
            telemetry_payload=payload,
            skew_us=abs(video_pts_us - telemetry_pts),
        )

    def _drop_stale(self, video_pts_us: int) -> None:
        cutoff = video_pts_us - self.tolerance_us
        while self._telemetry and self._telemetry[0][0] < cutoff:
            self._telemetry.popleft()

    def clear(self) -> None:
        self._telemetry.clear()

    def __len__(self) -> int:
        return len(self._telemetry)

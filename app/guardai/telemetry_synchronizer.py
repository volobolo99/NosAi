from __future__ import annotations

import collections
import logging
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FrameTelemetryPair:
    frame_id: int
    video_pts_us: int
    telemetry_pts_us: int
    telemetry_payload: dict[str, Any]
    skew_us: int


class GuardAiTelemetrySynchronizer:
    """Synchronize video PTS with Protobuf-derived telemetry in GuardAi.

    The buffer is bounded and malformed telemetry is rejected without raising,
    so a bad telemetry packet cannot interrupt the video rendering path.
    """

    def __init__(self, max_buffer_size: int = 120) -> None:
        if not isinstance(max_buffer_size, int) or isinstance(max_buffer_size, bool):
            raise ValueError("max_buffer_size must be an integer")
        if max_buffer_size <= 0:
            raise ValueError("max_buffer_size must be positive")
        self._max_buffer_size: int = max_buffer_size
        self._telemetry_buffer: dict[int, tuple[int, dict[str, Any]]] = {}
        self._pts_queue: collections.deque[tuple[int, int]] = collections.deque()
        self._last_skew_us: int = 0
        self._total_matched: int = 0
        self._total_dropped: int = 0

    def push_telemetry(
        self, frame_id: int, pts_us: int, payload: dict[str, Any]
    ) -> None:
        """Queue valid telemetry; malformed/stale duplicates are dropped fail-closed."""
        if (
            not isinstance(frame_id, int)
            or isinstance(frame_id, bool)
            or not isinstance(pts_us, int)
            or isinstance(pts_us, bool)
            or not isinstance(payload, dict)
        ):
            logger.error("Malformed telemetry packet: frame_id=%s, pts_us=%s", frame_id, pts_us)
            self._total_dropped += 1
            return
        if frame_id < 0 or pts_us < 0:
            logger.error("Invalid negative telemetry params: frame_id=%d, pts_us=%d", frame_id, pts_us)
            self._total_dropped += 1
            return
        if frame_id in self._telemetry_buffer:
            logger.debug("Duplicate telemetry packet ignored for frame_id=%d", frame_id)
            self._total_dropped += 1
            return
        if len(self._telemetry_buffer) >= self._max_buffer_size:
            _, oldest_frame_id = self._pts_queue.popleft()
            if self._telemetry_buffer.pop(oldest_frame_id, None) is not None:
                self._total_dropped += 1
        self._telemetry_buffer[frame_id] = (pts_us, dict(payload))
        self._pts_queue.append((pts_us, frame_id))

    def match_frame(
        self, frame_id: int, video_pts_us: int, tolerance_window_us: int = 16000
    ) -> Optional[FrameTelemetryPair]:
        """Return exact frame-id or nearest-PTS telemetry within the tolerance."""
        if (
            not isinstance(frame_id, int)
            or isinstance(frame_id, bool)
            or not isinstance(video_pts_us, int)
            or isinstance(video_pts_us, bool)
            or frame_id < 0
            or video_pts_us < 0
            or not isinstance(tolerance_window_us, int)
            or isinstance(tolerance_window_us, bool)
            or tolerance_window_us < 0
        ):
            return None

        exact = self._telemetry_buffer.pop(frame_id, None)
        if exact is not None:
            t_pts, payload = exact
            self._remove_frame_from_queue(frame_id)
            skew = abs(video_pts_us - t_pts)
            self._last_skew_us = skew
            if skew <= tolerance_window_us:
                self._total_matched += 1
                return FrameTelemetryPair(frame_id, video_pts_us, t_pts, payload, skew)
            self._total_dropped += 1
            logger.warning("Frame %d PTS skew %d us exceeded tolerance %d us", frame_id, skew, tolerance_window_us)
            return None

        best_frame_id: Optional[int] = None
        best_skew = tolerance_window_us + 1
        best_pts = 0
        best_payload: dict[str, Any] = {}
        for candidate_id, (candidate_pts, candidate_payload) in self._telemetry_buffer.items():
            skew = abs(video_pts_us - candidate_pts)
            if skew <= tolerance_window_us and (skew < best_skew or (skew == best_skew and candidate_pts < best_pts)):
                best_frame_id = candidate_id
                best_skew = skew
                best_pts = candidate_pts
                best_payload = candidate_payload
        if best_frame_id is not None:
            self._telemetry_buffer.pop(best_frame_id, None)
            self._remove_frame_from_queue(best_frame_id)
            self._last_skew_us = best_skew
            self._total_matched += 1
            return FrameTelemetryPair(frame_id, video_pts_us, best_pts, best_payload, best_skew)

        self._drop_stale(video_pts_us, tolerance_window_us)
        return None

    def _remove_frame_from_queue(self, frame_id: int) -> None:
        self._pts_queue = collections.deque(
            (pts, queued_id) for pts, queued_id in self._pts_queue if queued_id != frame_id
        )

    def _drop_stale(self, video_pts_us: int, tolerance_window_us: int) -> None:
        cutoff = video_pts_us - tolerance_window_us
        stale = [frame_id for frame_id, (pts, _) in self._telemetry_buffer.items() if pts < cutoff]
        for frame_id in stale:
            self._telemetry_buffer.pop(frame_id, None)
            self._remove_frame_from_queue(frame_id)
            self._total_dropped += 1

    @property
    def last_skew_us(self) -> int:
        return self._last_skew_us

    @property
    def total_matched(self) -> int:
        return self._total_matched

    @property
    def total_dropped(self) -> int:
        return self._total_dropped

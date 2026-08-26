"""Read-only NosTale perception and GameState normalization layer."""

from .gamestate import GameState, GameStateBuilder, PlayerState, WorldEntity
from .perception import Frame, FrameSource, ObservationPipeline, PerceptionResult
from .replay import ReplayFrame, ReplayFrameSource, write_jsonl
from .window_discovery import WindowCandidate, discover_windows
from .windows_backend import Win32WindowCaptureBackend
from .windows_capture import WindowsFrameSource, WindowsWindowTarget

__all__ = [
    "Frame", "FrameSource", "GameState", "GameStateBuilder", "PlayerState",
    "WorldEntity", "ObservationPipeline", "PerceptionResult", "ReplayFrame",
    "ReplayFrameSource", "write_jsonl", "WindowCandidate", "discover_windows",
    "WindowsFrameSource", "WindowsWindowTarget", "Win32WindowCaptureBackend",
]

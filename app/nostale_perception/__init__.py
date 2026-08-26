"""Read-only NosTale perception and GameState normalization layer.

The package converts client/window evidence into a deterministic, confidence-aware
GameState without executing game actions. Concrete capture/OCR/vision providers
are intentionally injected behind small interfaces.
"""

from .gamestate import GameState, GameStateBuilder, PlayerState, WorldEntity
from .perception import Frame, FrameSource, ObservationPipeline, PerceptionResult
from .windows_backend import Win32WindowCaptureBackend
from .windows_capture import WindowsFrameSource, WindowsWindowTarget

__all__ = [
    "Frame",
    "FrameSource",
    "GameState",
    "GameStateBuilder",
    "PlayerState",
    "WorldEntity",
    "ObservationPipeline",
    "PerceptionResult",
    "WindowsFrameSource",
    "WindowsWindowTarget",
    "Win32WindowCaptureBackend",
]

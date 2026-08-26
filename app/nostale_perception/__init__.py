"""Read-only NosTale perception and GameState normalization layer.

The package converts client/window evidence into a deterministic, confidence-aware
GameState without executing game actions. Concrete capture/OCR/vision providers
are intentionally injected behind small interfaces.
"""

from .gamestate import GameState, GameStateBuilder, PlayerState, WorldEntity
from .perception import Frame, FrameSource, ObservationPipeline, PerceptionResult

__all__ = [
    "Frame",
    "FrameSource",
    "GameState",
    "GameStateBuilder",
    "ObservationPipeline",
    "PerceptionResult",
    "PlayerState",
    "WorldEntity",
]

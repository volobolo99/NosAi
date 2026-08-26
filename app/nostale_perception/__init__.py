"""Read-only NosTale perception and GameState normalization layer."""

from .calibration import BarCalibration, CalibrationProfile, PlayerUiCalibration, Roi
from .dataset import DatasetManifest, build_manifest, sha256_file, write_manifest
from .evaluation import PerceptionEvaluation, evaluate
from .gamestate import GameState, GameStateBuilder, PlayerState, WorldEntity
from .ground_truth import FrameGroundTruth, load_ground_truth
from .metrics import NumericMetric, classification_accuracy, numeric_metric
from .perception import Frame, FrameSource, ObservationPipeline, PerceptionResult
from .replay import ReplayFrame, ReplayFrameSource, write_jsonl
from .ui_detector import BarObservation, PixelBarDetector
from .window_discovery import WindowCandidate, discover_windows
from .windows_backend import Win32WindowCaptureBackend
from .windows_capture import WindowsFrameSource, WindowsWindowTarget

__all__ = [
    "Frame", "FrameSource", "GameState", "GameStateBuilder", "PlayerState", "WorldEntity",
    "ObservationPipeline", "PerceptionResult", "ReplayFrame", "ReplayFrameSource", "write_jsonl",
    "Roi", "BarCalibration", "PlayerUiCalibration", "CalibrationProfile", "BarObservation",
    "PixelBarDetector", "WindowCandidate", "discover_windows", "WindowsFrameSource",
    "WindowsWindowTarget", "Win32WindowCaptureBackend", "FrameGroundTruth", "load_ground_truth",
    "NumericMetric", "numeric_metric", "classification_accuracy", "DatasetManifest", "build_manifest",
    "sha256_file", "write_manifest", "PerceptionEvaluation", "evaluate",
]

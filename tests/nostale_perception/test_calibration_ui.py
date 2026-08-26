from __future__ import annotations

from app.nostale_perception.calibration import BarCalibration, PlayerUiCalibration, Roi
from app.nostale_perception.perception import Frame
from app.nostale_perception.ui_detector import PixelBarDetector


def test_roi_maps_normalized_geometry_to_pixels() -> None:
    roi = Roi(0.25, 0.5, 0.5, 0.25)
    assert roi.pixels(100, 80) == (25, 40, 50, 20)


def test_bar_detector_uses_calibration_and_returns_bounded_value() -> None:
    # 4x1 BGRA frame: two filled, two empty pixels.
    pixels = b"\x00\x00\xff\xff" * 2 + b"\x00\x00\x00\xff" * 2
    frame = Frame("f1", 1, 4, 1, pixels, "test")
    calibration = BarCalibration(Roi(0, 0, 1, 1), 0, 100)
    detector = PixelBarDetector(calibration, lambda bgra: bgra[2] > 200)
    result = detector.detect(frame)
    assert result.value == 50
    assert result.maximum == 100
    assert result.fill_ratio == 0.5
    assert result.confidence > 0


def test_bar_detector_refuses_unknown_pixel_layout() -> None:
    frame = Frame("f1", 1, 4, 1, b"not-bgra", "test")
    calibration = BarCalibration(Roi(0, 0, 1, 1))
    result = PixelBarDetector(calibration, lambda _bgra: True).detect(frame)
    assert result.value is None
    assert result.confidence == 0


def test_player_ui_calibration_is_composable() -> None:
    profile = PlayerUiCalibration(
        hp=BarCalibration(Roi(0.1, 0.1, 0.2, 0.02), 0, 1000),
        mp=BarCalibration(Roi(0.1, 0.13, 0.2, 0.02), 0, 1000),
    )
    assert profile.hp is not None
    assert profile.mp is not None

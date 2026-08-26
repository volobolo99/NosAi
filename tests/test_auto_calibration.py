from pathlib import Path

import cv2
import numpy as np

from app.client.calibration import auto_calibrate


def test_auto_calibration_is_resolution_aware(tmp_path: Path):
    paths = []
    for i in range(3):
        image = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.rectangle(image, (40, 60), (1200, 600), (40 + i * 10, 80, 120), -1)
        cv2.rectangle(image, (1000, 20), (1250, 180), (180, 180, 180), -1)
        cv2.rectangle(image, (0, 580), (1280, 720), (90, 90, 90), -1)
        p = tmp_path / f"capture-{i}.png"
        assert cv2.imwrite(str(p), image)
        paths.append(p)

    out = tmp_path / "calibration.json"
    profile = auto_calibrate(paths, out)
    assert profile.width == 1280
    assert profile.height == 720
    assert profile.observation_only is True
    assert profile.status in {"candidate", "validated-baseline"}
    assert out.exists()


def test_auto_calibration_rejects_mixed_resolutions(tmp_path: Path):
    a = np.zeros((720, 1280, 3), dtype=np.uint8)
    b = np.zeros((1080, 1920, 3), dtype=np.uint8)
    pa, pb = tmp_path / "a.png", tmp_path / "b.png"
    assert cv2.imwrite(str(pa), a)
    assert cv2.imwrite(str(pb), b)
    try:
        auto_calibrate([pa, pb])
    except ValueError as exc:
        assert "same resolution" in str(exc)
    else:
        raise AssertionError("mixed resolutions must be rejected")

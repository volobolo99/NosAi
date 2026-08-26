import numpy as np
import pytest

from app.client.calibration import profile_for_resolution


def test_profile_is_observation_only():
    p = profile_for_resolution(1920, 1080)
    assert p.observation_only is True
    assert p.template_threshold >= 0.75


def test_profile_rejects_wrong_resolution():
    p = profile_for_resolution(1920, 1080)
    with pytest.raises(ValueError):
        p.validate_image(np.zeros((900, 1600, 3), dtype=np.uint8))


def test_profile_accepts_target_resolution():
    p = profile_for_resolution(1920, 1080)
    p.validate_image(np.zeros((1080, 1920, 3), dtype=np.uint8))

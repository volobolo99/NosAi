import pytest

from tools.windows_observation_e2e import WindowsObservationHarness


def test_harness_creates_output_directory(tmp_path):
    harness = WindowsObservationHarness(tmp_path / "obs")
    assert harness.output_dir.exists()
    assert harness.interval_s == 0.2


def test_harness_rejects_invalid_frame_count():
    with pytest.raises(ValueError):
        # Validation is intentionally performed by the CLI; this test documents
        # that the harness itself accepts only a positive interval.
        WindowsObservationHarness(".", interval_s=-1)

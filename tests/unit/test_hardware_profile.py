from app.hardware_profile import detect_hardware


def test_hardware_profile_is_conservative():
    profile = detect_hardware()
    assert profile.cpu_threads >= 1
    assert 2 <= profile.worker_threads <= 6
    assert profile.ram_budget_gb == 8.0
    assert profile.vram_budget_gb == 6.5
    assert profile.online_device == "cpu"
    assert profile.gpu_training_min_samples == 256

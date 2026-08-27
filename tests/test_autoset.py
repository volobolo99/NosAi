from __future__ import annotations

from app.autoset import AutoSetProfile, apply_process_settings, build_profile
from app.hardware_profile import HardwareProfile


def test_build_profile_is_conservative() -> None:
    hw = HardwareProfile(
        cpu_threads=16,
        worker_threads=6,
        ram_budget_gb=8.0,
        vram_budget_gb=6.5,
        online_device="cpu",
        training_device="cuda",
        gpu_training_min_samples=256,
    )
    profile = build_profile(hw)
    assert profile.worker_threads == 6
    assert profile.torch_threads == 4
    assert profile.online_device == "cpu"
    assert profile.training_device == "cuda"


def test_apply_process_settings_is_process_local(monkeypatch) -> None:
    profile = AutoSetProfile(
        platform="test",
        cpu_threads=8,
        worker_threads=4,
        ram_total_gb=16.0,
        ram_budget_gb=8.0,
        online_device="cpu",
        training_device="cpu",
        torch_threads=3,
    )
    monkeypatch.delenv("OMP_NUM_THREADS", raising=False)
    monkeypatch.delenv("MKL_NUM_THREADS", raising=False)
    applied = apply_process_settings(profile)
    assert applied["OMP_NUM_THREADS"] == 3
    assert applied["MKL_NUM_THREADS"] == 3
    assert applied["torch_threads"] in {None, 3}

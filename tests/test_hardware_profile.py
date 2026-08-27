from app.runtime.hardware_profile import HardwareProfile, recommend_local_model


def test_low_resource_profile_uses_4b():
    assert recommend_local_model(HardwareProfile(ram_gb=16, vram_gb=4)) == "qwen3:4b"


def test_mid_profile_uses_8b():
    assert recommend_local_model(HardwareProfile(ram_gb=32, vram_gb=8)) == "qwen3:8b"


def test_high_profile_uses_14b():
    assert recommend_local_model(HardwareProfile(ram_gb=64, vram_gb=24)) == "qwen3:14b"

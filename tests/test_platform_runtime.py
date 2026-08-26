from app.platform.capabilities import HardwareProfile
from app.platform.runtime import select_runtime


def profile(**overrides):
    values = dict(
        os_name="Windows", os_version="test", architecture="AMD64",
        python_version="3.12", cpu_count=16, ram_gb=32.0,
        gpu_names=("Test GPU",), npu_detected=False, directx_available=True,
        capture_backend="dxcam", cuda_available=True, torch_available=True,
        openai_key_present=True,
    )
    values.update(overrides)
    return HardwareProfile(**values)


def test_windows_gpu_hybrid_selection():
    runtime = select_runtime(profile())
    assert runtime.capture == "dxcam"
    assert runtime.perception == "torch-cuda"
    assert runtime.reasoning == "hybrid"
    assert runtime.openai_enabled is True


def test_no_openai_falls_back_to_local_reasoning():
    runtime = select_runtime(profile(openai_key_present=False))
    assert runtime.reasoning == "local-only"
    assert runtime.openai_enabled is False


def test_cpu_only_environment_is_supported():
    runtime = select_runtime(profile(torch_available=False, cuda_available=False, openai_key_present=False))
    assert runtime.perception == "cpu"
    assert runtime.reasoning == "local-only"
    assert runtime.mode == "compatibility"

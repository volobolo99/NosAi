from app.platform.capabilities import HardwareProfile
from app.platform.runtime import select_runtime


def profile(**overrides):
    values = dict(
        os_name="Windows",
        os_version="test",
        python_version="3.12",
        machine="AMD64",
        cpu_count=16,
        ram_gb=32.0,
        gpu_vendor="NVIDIA",
        gpu_name="Test GPU",
        gpu_vram_mb=8192,
        npu_present=True,
        directx_available=True,
        windows_graphics_available=True,
    )
    values.update(overrides)
    return HardwareProfile(**values)


def test_windows_gpu_selects_dxcam_and_accelerated_local_runtime():
    runtime = select_runtime(profile())
    assert runtime.capture_backend == "dxcam"
    assert runtime.inference_backend == "onnx-runtime"
    assert runtime.acceleration == "gpu-preferred"
    assert runtime.local_ai_enabled


def test_windows_without_gpu_selects_safe_cpu_runtime():
    runtime = select_runtime(profile(gpu_name=None, gpu_vendor=None, gpu_vram_mb=None))
    assert runtime.capture_backend == "dxcam"
    assert runtime.acceleration == "cpu"
    assert runtime.local_ai_enabled


def test_non_windows_uses_generic_capture_fallback():
    runtime = select_runtime(profile(os_name="Linux"))
    assert runtime.capture_backend == "generic"
    assert runtime.acceleration == "cpu"

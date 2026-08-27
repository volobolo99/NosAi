"""G3.25 coverage marker; detailed tests live in test_runtime_adapter.py."""

def test_g325_module_imports():
    from app.client.runtime_adapter import AdapterMode, RuntimeAdapter, RuntimeObservation
    assert AdapterMode.REAL.value == "real"
    assert RuntimeAdapter is not None
    assert RuntimeObservation is not None

from app.runtime.auto_config import AutoConfigurator


def test_autoset_persists_profile(tmp_path):
    service = AutoConfigurator(str(tmp_path / "autoconfig.json"))
    result = service.autoset()
    assert result["model"].startswith("qwen3:")
    assert (tmp_path / "autoconfig.json").exists()

import pytest

from app.ai.ollama_provider import OllamaProvider


@pytest.mark.asyncio
async def test_default_local_model_is_qwen3_4b(monkeypatch):
    monkeypatch.delenv("NOSAI_LOCAL_MODEL", raising=False)
    provider = OllamaProvider()
    assert provider.model == "qwen3:4b"
    assert provider.base_url == "http://127.0.0.1:11434"

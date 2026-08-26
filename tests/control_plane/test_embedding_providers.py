from unittest.mock import patch

from app.control_plane.embedding_providers import OllamaEmbeddingProvider, OpenAIEmbeddingProvider


def test_ollama_provider_uses_local_endpoint() -> None:
    provider = OllamaEmbeddingProvider(model_id="test-model", dimensions=3)
    payload = b'{"embeddings": [[1, 2, 3]]}'
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return payload
    with patch("urllib.request.urlopen", return_value=Response()) as mocked:
        assert provider.embed(["hello"]) == [[1.0, 2.0, 3.0]]
        assert mocked.call_args.kwargs["timeout"] == 120


def test_openai_provider_preserves_input_order() -> None:
    class Item:
        def __init__(self, index, embedding): self.index, self.embedding = index, embedding
    class Response:
        data = [Item(1, [2]), Item(0, [1])]
    class Client:
        class embeddings:
            @staticmethod
            def create(**kwargs): return Response()
    with patch("openai.OpenAI", return_value=Client()):
        provider = OpenAIEmbeddingProvider(dimensions=1)
        assert provider.embed(["a", "b"]) == [[1.0], [2.0]]

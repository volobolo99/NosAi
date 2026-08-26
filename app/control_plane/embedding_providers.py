"""Provider-neutral embedding adapters for the retrieval benchmark."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class EmbeddingProvider(Protocol):
    model_id: str
    dimensions: int

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


@dataclass(frozen=True, slots=True)
class OllamaEmbeddingProvider:
    """Ollama HTTP adapter; keeps local inference outside NosAi core."""
    model_id: str = "qwen3-embedding:0.6b"
    base_url: str = "http://127.0.0.1:11434"
    dimensions: int = 1024

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        import json
        from urllib.request import Request, urlopen

        if not texts:
            return []
        payload = json.dumps({"model": self.model_id, "input": list(texts)}).encode()
        request = Request(
            f"{self.base_url.rstrip('/')}/api/embed",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode())
        embeddings = body.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise RuntimeError("Ollama returned an invalid embedding response")
        return [[float(value) for value in vector] for vector in embeddings]


@dataclass(frozen=True, slots=True)
class OpenAIEmbeddingProvider:
    """OpenAI adapter loaded lazily so the core remains dependency-light."""
    model_id: str = "text-embedding-3-small"
    dimensions: int = 1536

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        from openai import OpenAI

        if not texts:
            return []
        client = OpenAI()
        response = client.embeddings.create(model=self.model_id, input=list(texts))
        ordered = sorted(response.data, key=lambda item: item.index)
        return [[float(value) for value in item.embedding] for item in ordered]

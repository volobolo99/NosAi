from app.control_plane.embeddings import HashEmbeddingProvider, cosine_similarity
from app.control_plane.memory_benchmark import RetrievalCase, RetrievalResult, precision_at_k, recall_at_k


def test_hash_embedding_is_deterministic_and_normalized() -> None:
    provider = HashEmbeddingProvider(32)
    first = provider.embed("sandbox timeout failure")
    second = provider.embed("sandbox timeout failure")
    assert first == second
    assert abs(cosine_similarity(first, second) - 1.0) < 1e-9


def test_retrieval_metrics() -> None:
    cases = [RetrievalCase("q", frozenset({"a", "b"}))]
    results = [RetrievalResult("q", ("a", "c"))]
    assert recall_at_k(cases, results, 2) == 0.5
    assert precision_at_k(cases, results, 2) == 0.5

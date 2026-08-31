"""Provider-neutral repository intelligence primitives.

The first implementation is intentionally deterministic and dependency-light.
It ranks repository candidates using task terms, path locality, file type and
simple symbol extraction. Future semantic/vector retrievers can implement the
same contract without changing the control plane.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import PurePosixPath
from typing import Iterable, Mapping, Protocol, Sequence


@dataclass(frozen=True, slots=True)
class RepositoryCandidate:
    path: str
    score: float
    reasons: tuple[str, ...] = ()
    symbols: tuple[str, ...] = ()


class RepositoryIndexer(Protocol):
    def index(self, files: Mapping[str, str]) -> Mapping[str, tuple[str, ...]]: ...


class RepositoryRetriever(Protocol):
    def retrieve(
        self,
        task: str,
        files: Mapping[str, str],
        *,
        limit: int = 12,
    ) -> Sequence[RepositoryCandidate]: ...


_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")
_PY_SYMBOL_RE = re.compile(r"^\\s*(?:async\\s+def|def|class)\\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)


def _tokens(value: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(value)}


def extract_symbols(path: str, content: str) -> tuple[str, ...]:
    """Extract stable, human-readable Python symbols without importing code."""
    if PurePosixPath(path).suffix != ".py":
        return ()
    return tuple(dict.fromkeys(_PY_SYMBOL_RE.findall(content)))


def build_index(files: Mapping[str, str]) -> Mapping[str, tuple[str, ...]]:
    """Build a lightweight symbol index suitable for deterministic retrieval."""
    return {path: extract_symbols(path, content) for path, content in files.items()}


def retrieve_repository_context(
    task: str,
    files: Mapping[str, str],
    *,
    limit: int = 12,
) -> Sequence[RepositoryCandidate]:
    """Rank relevant files deterministically; never execute repository code."""
    query = _tokens(task)
    index = build_index(files)
    ranked: list[RepositoryCandidate] = []

    for path, content in files.items():
        path_tokens = _tokens(path.replace("/", " ").replace("_", " ").replace("-", " "))
        content_tokens = _tokens(content)
        symbols = index[path]
        symbol_tokens = _tokens(" ".join(symbols))
        reasons: list[str] = []
        score = 0.0

        path_hits = query & path_tokens
        symbol_hits = query & symbol_tokens
        content_hits = query & content_tokens

        if path_hits:
            score += 5.0 * len(path_hits)
            reasons.append("path")
        if symbol_hits:
            score += 4.0 * len(symbol_hits)
            reasons.append("symbol")
        if content_hits:
            score += min(3.0, 0.5 * len(content_hits))
            reasons.append("content")
        if path.endswith(".py"):
            score += 0.25
        if path.startswith("tests/") and ("test" in query or "error" in query):
            score += 0.75
            reasons.append("test-surface")

        if score > 0:
            ranked.append(
                RepositoryCandidate(
                    path=path,
                    score=score,
                    reasons=tuple(reasons),
                    symbols=symbols,
                )
            )

    ranked.sort(key=lambda item: (-item.score, item.path))
    return ranked[: max(0, limit)]


class DeterministicRepositoryRetriever:
    """Default retriever used before optional semantic/vector adapters exist."""

    def retrieve(
        self,
        task: str,
        files: Mapping[str, str],
        *,
        limit: int = 12,
    ) -> Sequence[RepositoryCandidate]:
        return retrieve_repository_context(task, files, limit=limit)

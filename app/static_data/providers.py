"""Provider implementations for the NosAi data layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class Fetcher(Protocol):
    def __call__(self, dataset: str, timeout: float) -> Any: ...


@dataclass(frozen=True)
class ProviderConfig:
    timeout_seconds: float = 10.0
    version: str | None = None


class ProviderError(RuntimeError):
    """A provider could not return usable data."""


class HTTPDataProvider:
    """Transport-neutral HTTP provider with explicit provenance metadata."""

    name = "http"

    def __init__(self, fetcher: Fetcher, config: ProviderConfig | None = None) -> None:
        self._fetcher = fetcher
        self._config = config or ProviderConfig()

    @property
    def version(self) -> str | None:
        return self._config.version

    def fetch(self, dataset: str) -> Any:
        try:
            value = self._fetcher(dataset, self._config.timeout_seconds)
        except Exception as exc:
            raise ProviderError(f"HTTP provider failed for dataset '{dataset}'") from exc
        if value is None:
            raise ProviderError(f"HTTP provider returned no data for '{dataset}'")
        return value

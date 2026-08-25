"""Provider implementations for the NosAi data layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol


class Fetcher(Protocol):
    def __call__(self, dataset: str, timeout: float) -> Any: ...


@dataclass(frozen=True)
class ProviderConfig:
    timeout_seconds: float = 10.0


class ProviderError(RuntimeError):
    """A provider could not return usable data."""


class HTTPDataProvider:
    """Transport-neutral HTTP provider.

    The actual HTTP implementation is injected so the data layer remains easy
    to test and can later use the project's preferred HTTP client.
    """

    name = "http"

    def __init__(self, fetcher: Fetcher, config: ProviderConfig | None = None) -> None:
        self._fetcher = fetcher
        self._config = config or ProviderConfig()

    def fetch(self, dataset: str) -> Any:
        try:
            value = self._fetcher(dataset, self._config.timeout_seconds)
        except Exception as exc:
            raise ProviderError(f"HTTP provider failed for dataset '{dataset}'") from exc
        if value is None:
            raise ProviderError(f"HTTP provider returned no data for '{dataset}'")
        return value

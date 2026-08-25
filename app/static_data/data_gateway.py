"""Online-first data gateway for NosAi knowledge sources."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


class DataProvider(Protocol):
    name: str

    def fetch(self, dataset: str) -> Any:
        """Return the provider's latest representation of a dataset."""


@dataclass(frozen=True)
class CachePolicy:
    ttl_seconds: int
    allow_stale_fallback: bool = True


@dataclass
class CacheEntry:
    value: Any
    fetched_at: datetime
    source: str
    version: str | None = None

    @property
    def age_seconds(self) -> float:
        return max(0.0, (datetime.now(timezone.utc) - self.fetched_at).total_seconds())


class DataGateway:
    """Online-first gateway with stale fallback only for provider failures."""

    def __init__(self, provider: DataProvider, policies: dict[str, CachePolicy]) -> None:
        self._provider = provider
        self._policies = policies
        self._cache: dict[str, CacheEntry] = {}

    def get(self, dataset: str) -> Any:
        policy = self._policies.get(dataset, CachePolicy(ttl_seconds=300))
        try:
            value = self._provider.fetch(dataset)
        except Exception:
            entry = self._cache.get(dataset)
            if entry is not None and policy.allow_stale_fallback:
                return entry.value
            raise

        self._validate(dataset, value)
        self._cache[dataset] = CacheEntry(
            value=value,
            fetched_at=datetime.now(timezone.utc),
            source=self._provider.name,
        )
        return value

    def is_fresh(self, dataset: str) -> bool:
        entry = self._cache.get(dataset)
        if entry is None:
            return False
        policy = self._policies.get(dataset, CachePolicy(ttl_seconds=300))
        return entry.age_seconds <= policy.ttl_seconds

    @staticmethod
    def _validate(dataset: str, value: Any) -> None:
        if value is None:
            raise ValueError(f"Dataset '{dataset}' returned no data")

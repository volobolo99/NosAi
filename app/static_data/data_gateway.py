"""Online-first data gateway for NosAi knowledge sources.

The gateway centralizes remote access and keeps the runtime independent from
individual providers. Providers are responsible for transport/source access;
the gateway owns freshness, fallback and validation policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol


class DataProvider(Protocol):
    """Minimal provider contract used by the runtime data layer."""

    name: str

    def fetch(self, dataset: str) -> Any:
        """Return the provider's latest representation of a dataset."""


@dataclass(frozen=True)
class CachePolicy:
    """Freshness policy for a dataset."""

    ttl_seconds: int
    allow_stale_fallback: bool = True


@dataclass
class CacheEntry:
    """Validated value plus freshness metadata."""

    value: Any
    fetched_at: datetime
    source: str
    version: str | None = None

    @property
    def age_seconds(self) -> float:
        now = datetime.now(timezone.utc)
        return max(0.0, (now - self.fetched_at).total_seconds())


class DataGateway:
    """Central access point for static and online knowledge.

    Online-first means a fresh provider result is preferred. A previously
    validated value can be returned when the provider is temporarily
    unavailable and policy explicitly permits stale fallback.
    """

    def __init__(self, provider: DataProvider, policies: dict[str, CachePolicy]) -> None:
        self._provider = provider
        self._policies = policies
        self._cache: dict[str, CacheEntry] = {}

    def get(self, dataset: str) -> Any:
        policy = self._policies.get(dataset, CachePolicy(ttl_seconds=300))
        try:
            value = self._provider.fetch(dataset)
            self._validate(dataset, value)
            self._cache[dataset] = CacheEntry(
                value=value,
                fetched_at=datetime.now(timezone.utc),
                source=self._provider.name,
            )
            return value
        except Exception:
            entry = self._cache.get(dataset)
            if entry is not None and policy.allow_stale_fallback:
                return entry.value
            raise

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

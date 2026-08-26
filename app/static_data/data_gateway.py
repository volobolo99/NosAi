"""Online-first data gateway for NosAi knowledge sources."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
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
    """Online-first gateway with validated, optionally persistent stale fallback."""

    def __init__(
        self,
        provider: DataProvider,
        policies: dict[str, CachePolicy],
        cache_path: str | Path | None = None,
    ) -> None:
        self._provider = provider
        self._policies = policies
        self._cache_path = Path(cache_path) if cache_path is not None else None
        self._cache: dict[str, CacheEntry] = self._load_cache()

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
            version=getattr(self._provider, "version", None),
        )
        self._save_cache()
        return value

    def is_fresh(self, dataset: str) -> bool:
        entry = self._cache.get(dataset)
        if entry is None:
            return False
        policy = self._policies.get(dataset, CachePolicy(ttl_seconds=300))
        return entry.age_seconds <= policy.ttl_seconds

    def _load_cache(self) -> dict[str, CacheEntry]:
        if self._cache_path is None or not self._cache_path.is_file():
            return {}
        try:
            with self._cache_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict):
                return {}
            result: dict[str, CacheEntry] = {}
            for key, raw in payload.items():
                if not isinstance(key, str) or not isinstance(raw, dict):
                    continue
                timestamp = raw.get("fetched_at")
                if not isinstance(timestamp, str):
                    continue
                try:
                    fetched_at = datetime.fromisoformat(timestamp)
                except ValueError:
                    continue
                result[key] = CacheEntry(
                    value=raw.get("value"),
                    fetched_at=fetched_at,
                    source=str(raw.get("source", "")),
                    version=raw.get("version") if isinstance(raw.get("version"), str) else None,
                )
            return result
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return {}

    def _save_cache(self) -> None:
        if self._cache_path is None:
            return
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            key: {
                "value": entry.value,
                "fetched_at": entry.fetched_at.isoformat(),
                "source": entry.source,
                "version": entry.version,
            }
            for key, entry in self._cache.items()
        }
        fd, temporary = tempfile.mkstemp(
            prefix=f".{self._cache_path.name}.", dir=self._cache_path.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self._cache_path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    @staticmethod
    def _validate(dataset: str, value: Any) -> None:
        if value is None:
            raise ValueError(f"Dataset '{dataset}' returned no data")
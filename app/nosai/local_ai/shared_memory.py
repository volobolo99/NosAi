"""Controlled shared memory for primary/local AI cooperation."""
from dataclasses import dataclass
from threading import RLock
from typing import Any, Mapping

@dataclass(frozen=True)
class MemoryRecord:
    key: str
    value: Any
    source: str
    confidence: float
    version: int

class SharedMemory:
    """Authoritative store; AI proposals cannot mutate it implicitly."""
    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self._lock = RLock()

    def read(self, key: str) -> MemoryRecord | None:
        with self._lock:
            return self._records.get(key)

    def snapshot(self) -> Mapping[str, MemoryRecord]:
        with self._lock:
            return dict(self._records)

    def write(self, key: str, value: Any, *, source: str, confidence: float) -> MemoryRecord:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        with self._lock:
            previous = self._records.get(key)
            version = 1 if previous is None else previous.version + 1
            record = MemoryRecord(key, value, source, confidence, version)
            self._records[key] = record
            return record

    def apply_authorized_updates(self, updates: Mapping[str, Any], *, source: str, confidence: float) -> tuple[MemoryRecord, ...]:
        return tuple(self.write(k, v, source=source, confidence=confidence) for k, v in updates.items())

__all__ = ["MemoryRecord", "SharedMemory"]

"""Replay storage for offline learning and post-run analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import random
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class Transition:
    state: Mapping[str, Any]
    action: str
    reward: float
    next_state: Mapping[str, Any]
    terminated: bool = False
    truncated: bool = False
    info: Mapping[str, Any] | None = None


class ReplayBuffer:
    """Bounded, deterministic replay buffer with JSONL persistence."""

    def __init__(self, capacity: int = 100_000, seed: int = 42) -> None:
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._rng = random.Random(seed)
        self._items: list[Transition] = []

    def add(self, transition: Transition) -> None:
        self._items.append(transition)
        if len(self._items) > self.capacity:
            del self._items[: len(self._items) - self.capacity]

    def sample(self, batch_size: int) -> list[Transition]:
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        return self._rng.sample(self._items, min(batch_size, len(self._items)))

    def recent(self, limit: int = 100) -> list[Transition]:
        return self._items[-max(0, limit) :]

    def save_jsonl(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            for item in self._items:
                handle.write(json.dumps(asdict(item), ensure_ascii=False, sort_keys=True) + "\n")

    def load_jsonl(self, path: str | Path) -> int:
        loaded = 0
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                raw = json.loads(line)
                self.add(Transition(**raw))
                loaded += 1
        return loaded

    def __len__(self) -> int:
        return len(self._items)

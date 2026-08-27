"""Deterministic context construction for the local intelligence core."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .retrieval import MemoryMatch


@dataclass(frozen=True)
class ContextItem:
    """A retrieved memory plus its retrieval explanation."""

    memory: MemoryMatch


@dataclass(frozen=True)
class BuiltContext:
    """Bounded, deterministic context handed to the intelligence layer."""

    items: tuple[ContextItem, ...]
    text: str


class ContextBuilder:
    """Build a stable textual context without calling a model or external service."""

    def __init__(self, max_items: int = 5, max_chars: int = 6000) -> None:
        if max_items < 1:
            raise ValueError("max_items must be >= 1")
        if max_chars < 1:
            raise ValueError("max_chars must be >= 1")
        self.max_items = max_items
        self.max_chars = max_chars

    def build(self, matches: Sequence[MemoryMatch]) -> BuiltContext:
        selected = tuple(matches[: self.max_items])
        lines: list[str] = []
        included: list[ContextItem] = []
        for match in selected:
            record = match.record
            line = (
                f"state={record.state_fingerprint}; goal={record.goal.kind}; "
                f"action={record.intent.kind.value}; outcome={record.outcome.status}; "
                f"score={match.score:.4f}; reasons={','.join(match.reasons)}"
            )
            if len("\n".join(lines + [line])) > self.max_chars:
                break
            lines.append(line)
            included.append(ContextItem(match))
        return BuiltContext(items=tuple(included), text="\n".join(lines))

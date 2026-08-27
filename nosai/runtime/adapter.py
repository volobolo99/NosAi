"""Canonical runtime adapter boundary for NosAi G3.4.

Real execution is intentionally unavailable in this gate. Adapters may expose
capabilities and translate decisions into commands, but execution is denied
unless an explicitly enabled runtime implementation is introduced by a later
certified gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RuntimeCommand:
    action: str
    parameters: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class RuntimeResult:
    accepted: bool
    dry_run: bool
    message: str


class RuntimeAdapter(Protocol):
    def capabilities(self) -> frozenset[str]: ...
    def map_decision(self, action: str, parameters: dict[str, str] | None = None) -> RuntimeCommand: ...
    def execute(self, command: RuntimeCommand) -> RuntimeResult: ...


class DryRunRuntimeAdapter:
    """Deterministic adapter used for G3.4 certification."""

    def capabilities(self) -> frozenset[str]:
        return frozenset({"dry_run", "inspect", "simulate"})

    def map_decision(self, action: str, parameters: dict[str, str] | None = None) -> RuntimeCommand:
        if not action or not action.strip():
            raise ValueError("action must be non-empty")
        items = tuple(sorted((parameters or {}).items()))
        return RuntimeCommand(action=action.strip(), parameters=items)

    def execute(self, command: RuntimeCommand) -> RuntimeResult:
        return RuntimeResult(
            accepted=True,
            dry_run=True,
            message=f"simulated:{command.action}",
        )


class NosTaleRuntimeAdapter:
    """Safety-locked NosTale adapter skeleton.

    This class deliberately cannot execute real actions in G3.4.
    """

    def capabilities(self) -> frozenset[str]:
        return frozenset({"nos_tale", "prepared", "disabled"})

    def map_decision(self, action: str, parameters: dict[str, str] | None = None) -> RuntimeCommand:
        if not action or not action.strip():
            raise ValueError("action must be non-empty")
        return RuntimeCommand(action=action.strip(), parameters=tuple(sorted((parameters or {}).items())))

    def execute(self, command: RuntimeCommand) -> RuntimeResult:
        return RuntimeResult(
            accepted=False,
            dry_run=False,
            message="real NosTale execution is disabled in G3.4",
        )

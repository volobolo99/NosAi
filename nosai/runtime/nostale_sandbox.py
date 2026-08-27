"""NosTale runtime discovery and sandbox boundary for G3.8.

This module is deliberately observation/simulation only. It does not attach to,
control, inject into, or send input to an external process.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .adapter import RuntimeCommand, RuntimeResult


class RuntimeStatus(str, Enum):
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class RuntimeSnapshot:
    status: RuntimeStatus
    product: str
    version: str | None
    capabilities: frozenset[str]


class NosTaleSandboxAdapter:
    """Provider boundary that can describe a runtime without controlling it."""

    def __init__(self, product_name: str = "NosTale") -> None:
        self._product_name = product_name
        self._connected = False
        self._real_execution_enabled = False

    @property
    def real_execution_enabled(self) -> bool:
        return self._real_execution_enabled

    def discover(self, *, observed: bool = False, version: str | None = None) -> RuntimeSnapshot:
        if not observed:
            return RuntimeSnapshot(
                RuntimeStatus.UNKNOWN,
                self._product_name,
                None,
                frozenset({"discovery", "sandbox", "observation_only"}),
            )
        self._connected = True
        return RuntimeSnapshot(
            RuntimeStatus.AVAILABLE,
            self._product_name,
            version,
            frozenset({"discovery", "sandbox", "observation_only", "simulation"}),
        )

    def simulate(self, command: RuntimeCommand) -> RuntimeResult:
        if not self._connected:
            return RuntimeResult(False, True, "runtime discovery required")
        return RuntimeResult(True, True, f"nostale-sandbox:{command.action}")

    def execute(self, command: RuntimeCommand) -> RuntimeResult:
        return RuntimeResult(False, False, "real NosTale execution is disabled in G3.8")

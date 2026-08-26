"""Dashboard state adapter for the existing NosAi client contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.client.adapter import ClientAdapter


@dataclass
class DashboardState:
    connected: bool = False
    tick: int | None = None
    client: dict[str, Any] = field(default_factory=dict)
    world: dict[str, Any] = field(default_factory=dict)
    inventory: list[dict[str, Any]] = field(default_factory=list)
    goal: dict[str, Any] = field(default_factory=dict)
    decision: dict[str, Any] = field(default_factory=dict)
    performance: dict[str, Any] = field(default_factory=dict)
    last_error: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def snapshot_from_adapter(adapter: ClientAdapter) -> DashboardState:
    """Build a read-only dashboard snapshot from the normalized client state."""

    connected = adapter.check_connection()
    if not connected:
        return DashboardState(connected=False)

    state = adapter.read_state()
    payload = dict(state.payload)
    return DashboardState(
        connected=True,
        tick=state.tick,
        client=dict(payload.get("client", {})),
        world=dict(payload.get("world", {})),
        inventory=list(payload.get("inventory", [])),
        goal=dict(payload.get("goal", {})),
        decision=dict(payload.get("decision", {})),
        performance=dict(payload.get("performance", {})),
    )

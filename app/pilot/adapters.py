"""Safe adapters used by the Test Pilot.

The simulator deliberately implements the same public ClientAdapter contract as a
real client adapter, while never connecting to or controlling a game client.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.client.adapter import ClientState


@dataclass
class SimulatedClientAdapter:
    """Deterministic, side-effect-free client for local pilot tests."""

    scenario: str = "combat_basic"
    tick: int = 0
    connected: bool = True

    def check_connection(self) -> bool:
        return self.connected

    def read_state(self) -> ClientState:
        self.tick += 1
        if self.scenario == "combat_basic":
            payload: dict[str, Any] = {
                "player": {
                    "position": {"x": float(self.tick), "y": 0.0},
                    "hp": 100,
                    "mp": 80,
                },
                "entities": [
                    {"id": "target-1", "kind": "monster", "distance": 3.0, "hp": 100}
                ],
                "target": "target-1",
            }
        elif self.scenario == "missing_target":
            payload = {
                "player": {"position": {"x": 0.0, "y": 0.0}, "hp": 100, "mp": 80},
                "entities": [],
                "target": None,
            }
        elif self.scenario == "stale_state":
            payload = {"player": {"hp": 100, "mp": 80}}
        else:
            raise ValueError(f"unknown pilot scenario: {self.scenario}")
        return ClientState(tick=self.tick, payload=payload)

    def validate_action(self, action: Any) -> bool:
        """Validate without ever executing an action."""

        if not isinstance(action, dict):
            return False
        kind = action.get("type")
        return kind in {"observe", "attack", "wait", "none"}

    def close(self) -> None:
        self.connected = False

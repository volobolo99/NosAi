"""Orchestrator for the first safe NosAi Test Pilot."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any
import uuid

from app.client.adapter import ClientAdapter, validate_adapter
from app.self_repair.telemetry import TelemetryStore

from .event_store import PilotEventStore
from .models import PilotError, PilotResult, PilotSessionConfig, StateQuality
from .telemetry_schema import PilotEventType

DecisionFn = Callable[[dict[str, Any]], Any]


class TestPilot:
    """Run simulation/shadow observations and collect actionable diagnostics.

    This component deliberately has no method that executes an action. It only
    asks the adapter to *validate* a proposed action, preserving the safety
    boundary required before a real client integration exists.

    ``__test__ = False`` is intentional: the production runner is named
    ``TestPilot`` for domain/API compatibility, but it is not itself a pytest
    test class. This prevents pytest from attempting to collect it and removes
    a misleading collection warning during the environment gate.
    """

    __test__ = False

    def __init__(
        self,
        adapter: ClientAdapter,
        config: PilotSessionConfig | None = None,
        decision_fn: DecisionFn | None = None,
    ) -> None:
        """Validate dependencies and initialize the pilot session components."""
        validate_adapter(adapter)
        self.adapter = adapter
        self.config = config or PilotSessionConfig()
        self.decision_fn = decision_fn or self._baseline_decision
        self.telemetry = TelemetryStore(self.config.telemetry_path)
        self.events = PilotEventStore(self.config.event_path)

    @staticmethod
    def _baseline_decision(state: dict[str, Any]) -> dict[str, Any]:
        """Small deterministic baseline used only to exercise the pipeline."""

        target = state.get("target")
        entities = state.get("entities") or []
        if target and any(item.get("id") == target for item in entities if isinstance(item, dict)):
            return {"type": "attack", "target": target}
        return {"type": "wait"}

    @staticmethod
    def _missing_capabilities(
        payload: dict[str, Any], required: tuple[str, ...]
    ) -> tuple[str, ...]:
        """Return required dotted-path capabilities absent from the state payload."""
        missing: list[str] = []
        for capability in required:
            current: Any = payload
            for part in capability.split("."):
                if not isinstance(current, dict) or part not in current:
                    missing.append(capability)
                    break
                current = current[part]
        return tuple(missing)

    @staticmethod
    def _state_quality(missing: tuple[str, ...], required: tuple[str, ...]) -> StateQuality:
        """Classify state before the decision engine is allowed to run."""

        if not missing:
            return StateQuality.VALID
        critical = {"player.position", "entities", "target"}
        if critical.intersection(missing):
            return StateQuality.UNUSABLE
        return StateQuality.DEGRADED

    def run(self) -> PilotResult:
        """Execute the configured safe pilot loop and return collected diagnostics."""
        session_id = uuid.uuid4().hex
        errors: list[PilotError] = []
        latencies: list[float] = []
        decisions = 0
        valid_decisions = 0
        blocked_decisions = 0
        missing_seen: set[str] = set()
        state_quality_counts = {quality.value: 0 for quality in StateQuality}
        self.events.record(PilotEventType.SESSION_STARTED, session_id, payload={
            "mode": self.config.mode.value,
            "ticks": self.config.ticks,
        })

        if not self.adapter.check_connection():
            error = PilotError("C001", "client", "critical", "client adapter is not connected", False)
            errors.append(error)
            self.events.record(PilotEventType.ERROR, session_id, payload={
                "error_id": error.error_id, "component": error.component,
                "severity": error.severity, "message": error.message,
            })
            self.events.record(PilotEventType.SESSION_FINISHED, session_id, payload={
                "status": "ERROR", "ticks": 0, "decisions": 0,
            })
            return PilotResult(
                session_id, self.config.mode, 0, 0, 0, 0, state_quality_counts,
                tuple(errors), (), None
            )

        for tick_index in range(self.config.ticks):
            cycle_id = self.telemetry.start_cycle(
                "test_pilot", {"session_id": session_id, "mode": self.config.mode.value}
            )
            started = perf_counter()
            tick_errors: list[str] = []
            try:
                state = self.adapter.read_state()
                payload = state.payload
                missing = self._missing_capabilities(payload, self.config.required_capabilities)
                missing_seen.update(missing)
                quality = self._state_quality(missing, self.config.required_capabilities)
                state_quality_counts[quality.value] += 1
                self.events.record(
                    PilotEventType.STATE_OBSERVED,
                    session_id,
                    tick=tick_index,
                    state_quality=quality.value,
                    payload={"missing_capabilities": list(missing)},
                )

                if missing:
                    severity = "error" if quality is StateQuality.UNUSABLE else "warning"
                    error = PilotError(
                        "P001", "perception", severity,
                        "required state capabilities are missing", True,
                        {"missing_capabilities": missing, "state_quality": quality.value, "tick": state.tick},
                    )
                    errors.append(error)
                    tick_errors.append(error.error_id)
                    self.events.record(
                        PilotEventType.ERROR,
                        session_id,
                        tick=tick_index,
                        state_quality=quality.value,
                        payload={"error_id": error.error_id, **error.metadata},
                    )

                if quality is not StateQuality.VALID:
                    blocked_decisions += 1
                    self.events.record(
                        PilotEventType.DECISION_BLOCKED,
                        session_id,
                        tick=tick_index,
                        state_quality=quality.value,
                        payload={"reason": "state_quality", "missing_capabilities": list(missing)},
                    )
                    self.telemetry.finish_cycle(
                        cycle_id, "test_pilot", "BLOCKED",
                        (perf_counter() - started) * 1000.0,
                        {"state_quality": quality.value, "decision_blocked": True},
                        tuple(tick_errors),
                        {"session_id": session_id, "mode": self.config.mode.value, "missing_capabilities": missing},
                    )
                    continue

                decision_started = perf_counter()
                action = self.decision_fn(payload)
                latency_ms = (perf_counter() - decision_started) * 1000.0
                latencies.append(latency_ms)
                decisions += 1
                self.events.record(
                    PilotEventType.DECISION_PROPOSED,
                    session_id,
                    tick=tick_index,
                    state_quality=quality.value,
                    payload={"action": action, "latency_ms": latency_ms},
                )

                valid = self.adapter.validate_action(action)
                self.events.record(
                    PilotEventType.ACTION_VALIDATED,
                    session_id,
                    tick=tick_index,
                    state_quality=quality.value,
                    payload={"valid": valid, "action": action},
                )
                if valid:
                    valid_decisions += 1
                else:
                    error = PilotError(
                        "A001", "action", "error", "adapter rejected proposed action", True,
                        {"action": action, "tick": state.tick},
                    )
                    errors.append(error)
                    tick_errors.append(error.error_id)
                    self.events.record(PilotEventType.ERROR, session_id, tick=tick_index, payload={
                        "error_id": error.error_id, **error.metadata,
                    })

                self.telemetry.finish_cycle(
                    cycle_id, "test_pilot", "OK" if not tick_errors else "DEGRADED",
                    (perf_counter() - started) * 1000.0,
                    {"state_quality": quality.value, "tick": state.tick,
                     "decision_latency_ms": latency_ms, "action_valid": valid,
                     "decision_blocked": False},
                    tuple(tick_errors),
                    {"session_id": session_id, "action": action, "mode": self.config.mode.value},
                )
            except Exception as exc:  # noqa: BLE001 - pilot must capture runtime failures
                error = PilotError("C004", "client", "error", f"pilot cycle failed: {exc}", True,
                                   {"cycle_id": cycle_id, "tick": tick_index})
                errors.append(error)
                self.events.record(PilotEventType.ERROR, session_id, tick=tick_index, payload={
                    "error_id": error.error_id, **error.metadata, "message": error.message,
                })
                self.telemetry.finish_cycle(
                    cycle_id, "test_pilot", "ERROR", (perf_counter() - started) * 1000.0,
                    error_ids=(error.error_id,), metadata={"session_id": session_id},
                )

        self.events.record(PilotEventType.SESSION_FINISHED, session_id, payload={
            "status": "OK" if not errors else "DEGRADED",
            "ticks": self.config.ticks,
            "decisions": decisions,
            "blocked_decisions": blocked_decisions,
            "valid_decisions": valid_decisions,
        })
        return PilotResult(
            session_id=session_id, mode=self.config.mode, ticks=self.config.ticks,
            decisions=decisions, valid_decisions=valid_decisions,
            blocked_decisions=blocked_decisions, state_quality_counts=state_quality_counts,
            errors=tuple(errors), missing_capabilities=tuple(sorted(missing_seen)),
            avg_decision_latency_ms=(sum(latencies) / len(latencies)) if latencies else None,
        )

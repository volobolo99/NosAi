"""G3.25 layered runtime adapter with a strict observation boundary.

Modes are intentionally separated so replay and sandbox tests can run without
a live client. The REAL mode accepts only an injected ClientAdapter and uses
its read-only contract; this module never sends actions to a client.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from app.client.adapter import ClientAdapter, ClientState, validate_adapter


class AdapterMode(str, Enum):
    MOCK = "mock"
    REPLAY = "replay"
    SANDBOX = "sandbox"
    REAL = "real"


@dataclass(frozen=True)
class RuntimeObservation:
    tick: int
    payload: dict[str, Any]
    source: str


class RuntimeAdapter:
    """Normalize observations from mock, replay, sandbox, or live adapters."""

    def __init__(self, mode: AdapterMode, *, replay: Iterable[RuntimeObservation] = (),
                 sandbox_reader: Any = None, client: ClientAdapter | None = None):
        self.mode = AdapterMode(mode)
        self._replay = iter(replay)
        self._sandbox_reader = sandbox_reader
        self._client = client
        if self.mode is AdapterMode.SANDBOX and not callable(sandbox_reader):
            raise ValueError("sandbox mode requires a reader")
        if self.mode is AdapterMode.REAL:
            if client is None:
                raise ValueError("real mode requires an injected ClientAdapter")
            validate_adapter(client)

    def observe(self) -> RuntimeObservation:
        if self.mode is AdapterMode.MOCK:
            return RuntimeObservation(0, {"status": "mock", "observation_only": True}, "mock")
        if self.mode is AdapterMode.REPLAY:
            try:
                return next(self._replay)
            except StopIteration as exc:
                raise RuntimeError("replay exhausted") from exc
        if self.mode is AdapterMode.SANDBOX:
            state = self._sandbox_reader()
            return self._normalize(state, "sandbox")
        state = self._client.read_state()
        return self._normalize(state, "real")

    def connection_ok(self) -> bool:
        if self.mode in (AdapterMode.MOCK, AdapterMode.SANDBOX, AdapterMode.REPLAY):
            return True
        return bool(self._client.check_connection())

    def validate_dry_run(self) -> bool:
        if self.mode is AdapterMode.REAL:
            return bool(self._client.validate_action(None))
        return True

    @staticmethod
    def _normalize(state: Any, source: str) -> RuntimeObservation:
        if isinstance(state, ClientState):
            return RuntimeObservation(state.tick, dict(state.payload), source)
        if isinstance(state, dict):
            return RuntimeObservation(0, dict(state), source)
        raise TypeError("runtime observation must be ClientState or dict")

    def close(self) -> None:
        if self.mode is AdapterMode.REAL and self._client is not None:
            self._client.close()

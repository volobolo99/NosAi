"""Non-destructive live-client integration probe."""

from __future__ import annotations

from typing import Any

from .adapter import ClientState, validate_adapter


def run_client_probe(adapter: Any) -> list[tuple[str, str]]:
    """Exercise the live adapter without executing a game action.

    Returns ``(check_id, actual)`` pairs. Exceptions are intentionally allowed to
    propagate so the diagnostic layer can preserve the exact exception type and
    message.
    """

    validate_adapter(adapter)
    if adapter.check_connection() is not True:
        raise ConnectionError("client connection check returned a non-True result")

    state = adapter.read_state()
    if not isinstance(state, ClientState):
        raise TypeError("read_state() must return app.client.ClientState")
    if not isinstance(state.tick, int) or state.tick < 0:
        raise ValueError(f"invalid client state tick: {state.tick!r}")
    if not isinstance(state.payload, dict):
        raise TypeError("client state payload must be a dict")

    if adapter.validate_action(None) is not True:
        raise ValueError("validate_action(None) did not accept the non-destructive probe")

    return [
        ("CONNECTION", "CONNECTED"),
        ("STATE_READ", f"tick={state.tick}"),
        ("ACTION_VALIDATE", "DRY_RUN_OK"),
    ]

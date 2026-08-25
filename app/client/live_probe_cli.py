"""CLI for the real NosTale observation boundary; never sends game actions."""
from __future__ import annotations

import argparse
import json
from typing import Any

from .nostale_windows import NosTaleClientError, WindowsNosTaleAdapter


def run_probe(adapter: WindowsNosTaleAdapter) -> dict[str, Any]:
    result: dict[str, Any] = {
        "connected": False,
        "state_read": False,
        "process_names": list(adapter.process_names),
        "observation_only": True,
        "action_transport": "disabled",
    }
    try:
        result["connected"] = adapter.check_connection()
        if result["connected"]:
            result["state"] = adapter.read_state().payload
            result["state_read"] = True
    except NosTaleClientError as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe a running NosTale client safely")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    result = run_probe(WindowsNosTaleAdapter())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"connected: {result['connected']}")
        print(f"state_read: {result['state_read']}")
        print(f"process_names: {', '.join(result['process_names'])}")
        print("observation_only: true")
        print("action_transport: disabled")
        if result.get("state_read"):
            state = result["state"]
            rect = state["window_rect"]
            print(f"pid: {state['pid']}")
            print(f"window: {state['window_title']!r}")
            print(f"rect: {rect['width']}x{rect['height']} @ ({rect['left']}, {rect['top']})")
        elif "error" in result:
            print(f"error: {result['error']['type']}: {result['error']['message']}")
    return 0 if result["connected"] and result["state_read"] else 1

"""Reporting and post-session diagnostics for Test Pilot runs."""

from __future__ import annotations

import html
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import PilotResult


def result_to_dict(result: PilotResult) -> dict[str, Any]:
    """Return a stable, JSON-serializable result representation."""
    data = asdict(result)
    data["mode"] = result.mode.value
    # ``ready_for_live_action`` is a computed safety property, not a dataclass
    # field, so ``asdict`` does not include it. Persist it explicitly so JSON
    # and HTML reports expose the same safety gate without relying on a missing
    # dictionary key.
    data["ready_for_live_action"] = result.ready_for_live_action
    return data


def write_json_report(result: PilotResult, path: str | Path) -> Path:
    """Write the machine-readable session report."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result_to_dict(result), indent=2, sort_keys=True), encoding="utf-8")
    return target


def write_html_report(result: PilotResult, path: str | Path) -> Path:
    """Write a self-contained human-readable session report."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = result_to_dict(result)
    errors = data.get("errors", [])
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(error.get('error_id', '')))}</td>"
        f"<td>{html.escape(str(error.get('category', '')))}</td>"
        f"<td>{html.escape(str(error.get('message', '')))}</td>"
        "</tr>"
        for error in errors
    ) or "<tr><td colspan='3'>No errors recorded.</td></tr>"
    summary = "".join(
        f"<tr><th>{html.escape(key)}</th><td>{html.escape(str(value))}</td></tr>"
        for key, value in (
            ("session_id", data["session_id"]),
            ("mode", data["mode"]),
            ("ticks", data["ticks"]),
            ("decisions", data["decisions"]),
            ("valid_decisions", data["valid_decisions"]),
            ("blocked_decisions", data["blocked_decisions"]),
            ("state_quality_counts", data["state_quality_counts"]),
            ("missing_capabilities", data["missing_capabilities"]),
            ("avg_decision_latency_ms", data["avg_decision_latency_ms"]),
            ("ready_for_live_action", data["ready_for_live_action"]),
        )
    )
    target.write_text(
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>NosAi Test Pilot Report</title>"
        "<style>body{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{border:1px solid #ccc;padding:.5rem;text-align:left}"
        "code{background:#f4f4f4;padding:.1rem .3rem}</style></head><body>"
        "<h1>NosAi Test Pilot Report</h1>"
        f"<h2>Session <code>{html.escape(str(data['session_id']))}</code></h2>"
        f"<table>{summary}</table><h2>Errors</h2><table>"
        "<tr><th>ID</th><th>Category</th><th>Message</th></tr>"
        f"{rows}</table></body></html>",
        encoding="utf-8",
    )
    return target

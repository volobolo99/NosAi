"""M1 orchestration: integrity -> governance/evidence readiness.

This module is intentionally side-effect free. It creates a deterministic
preflight result; actual Windows execution remains an explicit runtime gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .runtime_manifest import build_manifest
from .runtime_payload import PayloadVerification, verify_payload


@dataclass(frozen=True, slots=True)
class M1Preflight:
    payload: PayloadVerification
    manifest_entries: int
    ready_for_windows_execution: bool


def preflight_payload(root: Path) -> M1Preflight:
    manifest = build_manifest(root)
    verification = verify_payload(root, manifest)
    return M1Preflight(
        payload=verification,
        manifest_entries=len(manifest),
        ready_for_windows_execution=verification.passed and bool(manifest),
    )

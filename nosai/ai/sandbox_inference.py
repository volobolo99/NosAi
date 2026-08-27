"""Bounded, offline inference sandbox for G3.24.

The sandbox accepts a callable supplied by the host test harness. It does not
load arbitrary artifacts, spawn processes, access the network, or control the
OS/game runtime.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import time
from typing import Any, Callable


@dataclass(frozen=True)
class InferenceEvidence:
    request_id: str
    model_id: str
    model_version: str
    input_digest: str
    output_digest: str
    latency_ms: float
    success: bool
    error: str | None = None

    def canonical(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))

    def digest(self) -> str:
        return sha256(self.canonical().encode()).hexdigest()


class SandboxError(RuntimeError):
    pass


class InferenceSandbox:
    """Small deterministic boundary around a caller-provided pure inference function."""

    def __init__(self, *, max_input_bytes: int = 1_048_576, timeout_seconds: float = 2.0):
        if max_input_bytes <= 0 or timeout_seconds <= 0:
            raise ValueError("sandbox limits must be positive")
        self.max_input_bytes = max_input_bytes
        self.timeout_seconds = timeout_seconds

    def infer(self, request_id: str, model_id: str, model_version: str,
              payload: Any, inference_fn: Callable[[Any], Any]) -> tuple[Any | None, InferenceEvidence]:
        if not request_id or not model_id or not model_version:
            raise ValueError("request_id, model_id and model_version are required")
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
        if len(encoded) > self.max_input_bytes:
            raise SandboxError("input exceeds sandbox limit")
        start = time.perf_counter()
        try:
            output = inference_fn(payload)
            elapsed = time.perf_counter() - start
            if elapsed > self.timeout_seconds:
                raise SandboxError("inference exceeded sandbox timeout")
            output_encoded = json.dumps(output, sort_keys=True, separators=(",", ":"), default=str).encode()
            evidence = InferenceEvidence(request_id, model_id, model_version,
                sha256(encoded).hexdigest(), sha256(output_encoded).hexdigest(),
                elapsed * 1000.0, True)
            return output, evidence
        except Exception as exc:
            elapsed = time.perf_counter() - start
            evidence = InferenceEvidence(request_id, model_id, model_version,
                sha256(encoded).hexdigest(), sha256(b"").hexdigest(),
                elapsed * 1000.0, False, type(exc).__name__)
            return None, evidence

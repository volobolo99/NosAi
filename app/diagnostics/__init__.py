"""Runtime diagnostics and pre-flight validation."""

from .preflight import CheckResult, PreflightReport, run_preflight

__all__ = ["CheckResult", "PreflightReport", "run_preflight"]

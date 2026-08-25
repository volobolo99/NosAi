"""Runtime diagnostics and pre-flight validation."""

from .collector import collect_diagnostics, write_report
from .preflight import CheckResult, PreflightReport, run_preflight

__all__ = [
    "CheckResult",
    "PreflightReport",
    "collect_diagnostics",
    "run_preflight",
    "write_report",
]

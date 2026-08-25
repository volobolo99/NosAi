"""Deterministic startup checks with machine-readable diagnostics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib
import json
import platform
import sys
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class CheckResult:
    """Result of one pre-flight check."""

    check_id: str
    phase: str
    status: str
    severity: str
    message: str
    expected: str = ""
    actual: str = ""
    error_type: str = ""
    exception: str = ""

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


@dataclass(frozen=True)
class PreflightReport:
    """Complete pre-flight result; safe to serialize to JSON."""

    status: str
    checks: tuple[CheckResult, ...]

    @property
    def passed(self) -> bool:
        return self.status == "READY"

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "checks": [asdict(c) for c in self.checks]}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


_DEFAULT_MODULES = (
    "app",
    "app.client",
    "app.diagnostics",
    "app.m1",
    "app.m2",
    "app.m3",
    "app.m4",
    "app.m5",
    "app.m6",
    "app.m7",
    "app.m8",
    "app.m9",
    "app.m10",
    "app.m11",
    "app.m12",
    "app.m13",
    "app.m14",
    "app.m15",
)


def _run_check(
    check_id: str,
    phase: str,
    fn: Callable[[], str],
    expected: str,
    severity: str = "ERROR",
) -> CheckResult:
    try:
        actual = fn()
        return CheckResult(check_id, phase, "PASS", "INFO", "OK", expected, actual)
    except Exception as exc:  # noqa: BLE001 - diagnostics must report every startup failure.
        return CheckResult(
            check_id,
            phase,
            "FAIL",
            severity,
            str(exc),
            expected,
            "",
            type(exc).__name__,
            repr(exc),
        )


def _check_python() -> str:
    if sys.version_info < (3, 10):
        raise RuntimeError(f"Python {platform.python_version()} is below required 3.10")
    return platform.python_version()


def _check_module(name: str) -> Callable[[], str]:
    def check() -> str:
        importlib.import_module(name)
        return name

    return check


def _check_torch() -> str:
    torch = importlib.import_module("torch")
    return str(torch.__version__)


def _check_client(adapter: Any) -> str:
    from app.client.probe import run_client_probe

    probe = run_client_probe(adapter)
    return ",".join(f"{name}={value}" for name, value in probe)


def run_preflight(
    *,
    client_adapter: Any = None,
    modules: Iterable[str] = _DEFAULT_MODULES,
    require_client: bool = False,
    require_torch: bool = True,
) -> PreflightReport:
    """Run startup checks without executing game actions.

    When ``require_client`` is true, the adapter is connected, a normalized state
    is read, and a dry-run action validation is performed. No game action is sent.
    """

    checks: list[CheckResult] = [
        _run_check(
            "NOSAI-ENV-0001",
            "ENVIRONMENT",
            _check_python,
            "Python >= 3.10",
        )
    ]

    if require_torch:
        checks.append(
            _run_check(
                "NOSAI-DEP-0001",
                "DEPENDENCIES",
                _check_torch,
                "PyTorch importable",
            )
        )

    for module in modules:
        checks.append(
            _run_check(
                f"NOSAI-MOD-{module.replace('.', '-').upper()}",
                "MODULE_IMPORT",
                _check_module(module),
                f"module {module} importable",
            )
        )

    client_result = _run_check(
        "NOSAI-CLIENT-0001",
        "CLIENT_INTEGRATION",
        lambda: _check_client(client_adapter),
        "connected client with readable state and dry-run action validation"
        if require_client
        else "client optional",
    )
    if not require_client:
        client_result = CheckResult(
            client_result.check_id,
            client_result.phase,
            "SKIP",
            "INFO",
            "Client integration not configured",
            "client optional",
            "NOT_CONFIGURED",
        )
    elif client_result.status == "FAIL":
        client_result = CheckResult(
            client_result.check_id,
            client_result.phase,
            "FAIL",
            "BLOCKER",
            client_result.message,
            client_result.expected,
            client_result.actual,
            client_result.error_type,
            client_result.exception,
        )
    checks.append(client_result)

    blocking = any(c.status == "FAIL" and c.severity in {"ERROR", "BLOCKER"} for c in checks)
    return PreflightReport("BLOCKED" if blocking else "READY", tuple(checks))

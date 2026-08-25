from app.diagnostics import run_preflight


class HealthyClient:
    def check_connection(self):
        return True


class BrokenClient:
    def check_connection(self):
        raise RuntimeError("client transport unavailable")


def test_preflight_without_client_is_ready():
    report = run_preflight(modules=("app",), require_client=False, require_torch=False)
    assert report.status == "READY"
    assert any(c.status == "SKIP" for c in report.checks)


def test_preflight_connected_client_is_ready():
    report = run_preflight(
        client_adapter=HealthyClient(),
        modules=("app",),
        require_client=True,
        require_torch=False,
    )
    assert report.status == "READY"
    client = next(c for c in report.checks if c.check_id == "NOSAI-CLIENT-0001")
    assert client.status == "PASS"


def test_preflight_client_failure_is_blocking_and_diagnostic():
    report = run_preflight(
        client_adapter=BrokenClient(),
        modules=("app",),
        require_client=True,
        require_torch=False,
    )
    assert report.status == "BLOCKED"
    client = next(c for c in report.checks if c.check_id == "NOSAI-CLIENT-0001")
    assert client.status == "FAIL"
    assert client.severity == "BLOCKER"
    assert client.error_type == "RuntimeError"
    assert "client transport unavailable" in client.exception

from __future__ import annotations

from app.dashboard.events import DashboardEventBus
from app.dashboard.runtime_bridge import publish_runtime_trace


class FakeAdapter:
    def check_connection(self) -> bool:
        return True

    def read_state(self):
        class State:
            tick = 1
            payload = {
                "decision": {
                    "trace": [{"stato": "ok", "valore": i} for i in range(15)]
                }
            }

        return State()


def test_runtime_trace_publishes_all_m1_m15_modules() -> None:
    bus = DashboardEventBus()
    events = publish_runtime_trace(FakeAdapter(), bus)
    assert [event.dati["modulo"] for event in events] == [f"M{i}" for i in range(1, 16)]
    assert all(event.dati["fonte_trace"] == "runtime" for event in events)


def test_runtime_trace_does_not_invent_missing_modules() -> None:
    class MissingTraceAdapter(FakeAdapter):
        def read_state(self):
            class State:
                tick = 1
                payload = {"decision": {}}

            return State()

    events = publish_runtime_trace(MissingTraceAdapter(), DashboardEventBus())
    assert len(events) == 15
    assert all(event.dati["fonte_trace"] == "non_disponibile" for event in events)
    assert all(event.dati["riepilogo"]["stato"] == "non disponibile" for event in events)

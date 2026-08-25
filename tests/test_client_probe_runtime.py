from app.client import ClientState
from app.client.adapter_runtime import probe_client


class HealthyClient:
    def check_connection(self):
        return True

    def read_state(self):
        return ClientState(tick=7, payload={"player": {"hp": 100}})

    def validate_action(self, action):
        return action is None


def test_probe_is_non_destructive_and_validates_state_and_dry_run():
    client = HealthyClient()
    result = probe_client(client)
    assert result.connected is True
    assert result.state_valid is True
    assert result.action_valid is True
    assert result.detail.startswith("connected")

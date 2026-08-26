from app.ai.providers import OpenAIProvider


class FakeResponse:
    output_text = '{"action_type":"plan","valid":true,"confidence":0.92,"rationale":"safe"}'


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_openai_provider_uses_responses_api_and_normalizes_result():
    client = FakeClient()
    provider = OpenAIProvider(model="gpt-test", client=client)

    result = provider.decide({"hp": 100}, "survive")

    assert result["provider"] == "openai"
    assert result["action_type"] == "plan"
    assert result["confidence"] == 0.92
    assert client.responses.calls[0]["model"] == "gpt-test"
    assert "survive" in client.responses.calls[0]["input"]

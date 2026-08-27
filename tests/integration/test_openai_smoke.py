"""Minimal live OpenAI smoke test for CI.

This test is intentionally separate from the normal regression suite. It
verifies that GitHub Actions can authenticate to OpenAI and receive a small
Responses API result. It never invokes NosTale, action transport, tools, or
computer control.
"""

import os

import pytest


@pytest.mark.integration
def test_openai_responses_api_smoke():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY is not configured in the CI environment")

    from openai import OpenAI

    client = OpenAI(api_key=api_key, timeout=30.0, max_retries=1)
    model = os.getenv("NOSAI_OPENAI_MODEL", "gpt-5.2")
    response = client.responses.create(
        model=model,
        input="Return exactly the word OK.",
        max_output_tokens=16,
    )

    assert response.output_text.strip() == "OK", "OpenAI did not return the expected smoke-test output"

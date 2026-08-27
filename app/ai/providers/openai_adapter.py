"""OpenAI provider boundary.

This module intentionally contains no live API call yet. Credential wiring is
performed only after the secure API-key destination is confirmed.
"""
from __future__ import annotations

from typing import Any


class OpenAIAdapter:
    provider_name = "openai"

    def __init__(self, client: Any) -> None:
        self._client = client

    def client(self) -> Any:
        return self._client

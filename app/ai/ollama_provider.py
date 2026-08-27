"""Local Ollama provider for zero-API-cost NosAi inference.

The provider is optional and injected behind AIGateway. It never executes
NosTale actions. If Ollama is unavailable, the gateway can use its fallback.
"""
from __future__ import annotations

import json
import os
from urllib import request

from app.ai.contracts import ActionIntent, ActionKind, Decision


class OllamaProvider:
    name = "ollama"

    def __init__(self, model: str | None = None, base_url: str | None = None, timeout: float = 8.0) -> None:
        self.model = model or os.getenv("NOSAI_LOCAL_MODEL", "qwen3:4b")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.timeout = timeout

    async def decide(self, context: dict) -> Decision:
        # Keep transport dependency-free for the base project; callers can
        # run this provider in an executor if used from an async event loop.
        prompt = json.dumps(context, ensure_ascii=False, separators=(",", ":"))
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        req = request.Request(f"{self.base_url}/api/generate", data=payload, headers={"Content-Type": "application/json"})
        with request.urlopen(req, timeout=self.timeout) as response:
            data = json.loads(response.read().decode())
        text = data.get("response", "").strip()
        if not text:
            raise RuntimeError("Ollama returned an empty response")
        # Initial integration is proposal-only: do not let free-form model
        # output become an executable game action.
        return Decision(ActionIntent(ActionKind.WAIT), 0.0, f"ollama:{self.model}:proposal-only")

"""Live research providers for Simulation & Repair.

Research is evidence collection only: returned material is never executed and
never treated as a trusted solution. Network access is explicit and bounded.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ResearchHit:
    title: str
    url: str
    source_type: str
    excerpt: str = ""
    repository: str | None = None


class ResearchError(RuntimeError):
    """A research provider failed without producing trustworthy evidence."""


class GitHubResearchProvider:
    """Search public GitHub repositories/code without executing remote content.

    Authentication is optional. Set GITHUB_TOKEN for the higher authenticated
    API budget. The provider deliberately returns metadata/snippets only.
    """

    def __init__(self, token: str | None = None, timeout: float = 8.0, retries: int = 2) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout
        self.retries = max(0, retries)

    def search(self, query: str, *, limit: int = 8) -> list[ResearchHit]:
        if not query.strip():
            return []
        limit = max(1, min(limit, 20))
        url = f"https://api.github.com/search/code?q={quote(query)}&per_page={limit}"
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "NosAi-SimulationResearch/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                request = Request(url, headers=headers, method="GET")
                with urlopen(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                return [
                    ResearchHit(
                        title=str(item.get("name", "unknown")),
                        url=str(item.get("html_url", "")),
                        source_type="github_code",
                        excerpt="",
                        repository=(item.get("repository") or {}).get("full_name"),
                    )
                    for item in payload.get("items", [])
                    if item.get("html_url")
                ]
            except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(0.5 * (2**attempt))
        raise ResearchError(f"GitHub research failed: {last_error}") from last_error


def build_research_queries(error_type: str, message: str, component: str = "") -> list[str]:
    """Build bounded, reproducible search queries from an error event."""
    parts = [p.strip() for p in (error_type, message, component) if p and p.strip()]
    if not parts:
        return []
    queries = [" ".join(parts[:2])]
    if component:
        queries.append(f"{error_type} {component}")
    if message and message != error_type:
        queries.append(f'"{message[:120]}" {error_type}')
    return list(dict.fromkeys(queries))

"""Live, bounded research providers for Simulation & Repair.

Research is evidence collection only: returned material is never executed and
never treated as a trusted solution. Network access is explicit and bounded.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ResearchHit:
    title: str
    url: str
    source_type: str
    excerpt: str = ""
    repository: str | None = None
    license: str | None = None
    score: float | None = None


class ResearchError(RuntimeError):
    """A research provider failed without producing trustworthy evidence."""


class _HttpJsonClient:
    def __init__(self, *, timeout: float = 8.0, retries: int = 2, user_agent: str = "NosAi-SimulationResearch/2.0") -> None:
        self.timeout = timeout
        self.retries = max(0, retries)
        self.user_agent = user_agent

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> dict:
        request_headers = {"Accept": "application/json", "User-Agent": self.user_agent, **(headers or {})}
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                request = Request(url, headers=request_headers, method="GET")
                with urlopen(request, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                last_error = exc
                if exc.code in {403, 429} and attempt < self.retries:
                    retry_after = exc.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 1.0 * (2**attempt))
                elif attempt < self.retries and exc.code >= 500:
                    time.sleep(0.5 * (2**attempt))
                else:
                    break
            except (URLError, TimeoutError, ValueError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(0.5 * (2**attempt))
        raise ResearchError(f"Research request failed: {last_error}") from last_error


class GitHubResearchProvider:
    """Search public GitHub repositories/code without executing remote content."""

    def __init__(self, token: str | None = None, timeout: float = 8.0, retries: int = 2) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.client = _HttpJsonClient(timeout=timeout, retries=retries)

    def search(self, query: str, *, limit: int = 8) -> list[ResearchHit]:
        if not query.strip():
            return []
        limit = max(1, min(limit, 20))
        url = f"https://api.github.com/search/code?q={quote(query)}&per_page={limit}"
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2026-03-10"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        payload = self.client.get(url, headers=headers)
        hits: list[ResearchHit] = []
        for item in payload.get("items", []):
            repository = (item.get("repository") or {}).get("full_name")
            hits.append(ResearchHit(
                title=str(item.get("name", "unknown")),
                url=str(item.get("html_url", "")),
                source_type="github_code",
                repository=repository,
                score=float((item.get("repository") or {}).get("stargazers_count", 0) or 0),
            ))
        return [hit for hit in hits if hit.url]


class StackOverflowResearchProvider:
    """Search Stack Overflow through the official Stack Exchange API."""

    def __init__(self, *, site: str = "stackoverflow", key: str | None = None, timeout: float = 8.0, retries: int = 2) -> None:
        self.site = site
        self.key = key or os.getenv("STACKEXCHANGE_KEY")
        self.client = _HttpJsonClient(timeout=timeout, retries=retries)

    def search(self, query: str, *, limit: int = 8) -> list[ResearchHit]:
        if not query.strip():
            return []
        params = {"site": self.site, "intitle": query[:120], "sort": "relevance", "pagesize": max(1, min(limit, 20))}
        if self.key:
            params["key"] = self.key
        payload = self.client.get("https://api.stackexchange.com/2.3/search/advanced?" + urlencode(params))
        hits: list[ResearchHit] = []
        for item in payload.get("items", []):
            url = str(item.get("link", ""))
            if url:
                hits.append(ResearchHit(
                    title=str(item.get("title", "unknown")),
                    url=url,
                    source_type="stackoverflow_question",
                    excerpt=str(item.get("title", "")),
                    score=float(item.get("score", 0) or 0),
                ))
        return hits


class MultiSourceResearchProvider:
    """Bounded fan-out across approved programming sources with deduplication."""

    def __init__(self, providers: tuple[object, ...] | None = None) -> None:
        self.providers = providers or (GitHubResearchProvider(), StackOverflowResearchProvider())

    def search(self, queries: list[str], *, per_provider: int = 6, total_limit: int = 16) -> list[ResearchHit]:
        seen: set[str] = set()
        hits: list[ResearchHit] = []
        for query in queries:
            for provider in self.providers:
                search = getattr(provider, "search")
                try:
                    results = search(query, limit=per_provider)
                except ResearchError:
                    continue
                for hit in results:
                    if hit.url and hit.url not in seen:
                        seen.add(hit.url)
                        hits.append(hit)
                        if len(hits) >= total_limit:
                            return hits
        return hits


def build_research_queries(error_type: str, message: str, component: str = "", *, limit: int = 6) -> list[str]:
    """Build bounded, reproducible search queries from an error event."""
    parts = [p.strip() for p in (error_type, message, component) if p and p.strip()]
    if not parts:
        return []
    raw = [
        " ".join(parts[:2]),
        f"{error_type} {component}" if component else "",
        f'"{message[:120]}" {error_type}' if message and message != error_type else "",
        f"{error_type} Python fix",
        f"{error_type} Windows Python",
        f"{component} {error_type} regression" if component else "",
    ]
    return list(dict.fromkeys(q.strip() for q in raw if q.strip()))[: max(1, min(limit, 12))]

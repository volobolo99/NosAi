"""Safe online research adapter.

The Evolution Lab consumes normalized findings; network failures are explicit
and never become implicit evidence. Secrets are supplied by the host process.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import json

from .research import ResearchFinding, ResearchResult, rank_findings


@dataclass(frozen=True, slots=True)
class OnlineResearchConfig:
    endpoint: str
    user_agent: str = "NosAi-EvolutionLab/1.0"
    timeout_seconds: float = 10.0


class OnlineResearchError(RuntimeError):
    """Raised when an online research request cannot produce valid findings."""


def search_json(config: OnlineResearchConfig, query: str) -> ResearchResult:
    url = config.endpoint.rstrip("/") + "?q=" + quote_plus(query)
    request = Request(url, headers={"User-Agent": config.user_agent, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=config.timeout_seconds) as response:  # nosec B310: endpoint is operator-configured
            payload = json.load(response)
    except Exception as exc:  # noqa: BLE001 - normalize transport/provider failures
        raise OnlineResearchError(f"research provider failed: {type(exc).__name__}") from exc

    raw_items = payload.get("findings", []) if isinstance(payload, dict) else []
    findings: list[ResearchFinding] = []
    for item in raw_items:
        if not isinstance(item, dict) or not item.get("finding_id") or not item.get("source"):
            continue
        findings.append(
            ResearchFinding(
                finding_id=str(item["finding_id"]),
                source=str(item["source"]),
                title=str(item.get("title", "")),
                summary=str(item.get("summary", "")),
                url=str(item["url"]) if item.get("url") else None,
                relevance=float(item.get("relevance", 0.0)),
                reliability=float(item.get("reliability", 0.0)),
                freshness=float(item.get("freshness", 0.0)),
            )
        )
    return ResearchResult(query=query, findings=rank_findings(findings))

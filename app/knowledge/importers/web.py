"""Conservative web-document importer.

It is deliberately allowlist-based and read-only. It extracts visible text from
HTML without executing scripts, then stores a bounded evidence excerpt.
"""
from __future__ import annotations

import re
import urllib.request
from dataclasses import dataclass
from hashlib import sha256
from html import unescape

from ..models import Evidence, KnowledgeNode, NodeType
from ..store import KnowledgeStore


@dataclass(frozen=True)
class WebDocument:
    url: str
    title: str | None = None
    version: str | None = None


class WebImporter:
    def __init__(self, store: KnowledgeStore, timeout: int = 20, max_bytes: int = 2_000_000) -> None:
        self.store = store
        self.timeout = timeout
        self.max_bytes = max_bytes

    def import_document(self, document: WebDocument) -> int:
        request = urllib.request.Request(
            document.url,
            headers={"User-Agent": "NosAi-KnowledgeImporter/1.0", "Accept": "text/html,text/plain;q=0.9"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            raw = response.read(self.max_bytes + 1)
            content_type = response.headers.get_content_type()
        if len(raw) > self.max_bytes:
            raise ValueError("web document exceeds configured size limit")
        text = raw.decode("utf-8", errors="replace")
        if content_type == "text/html":
            text = self._html_to_text(text)
        digest = sha256(raw).hexdigest()
        node_id = "web:" + sha256(document.url.encode("utf-8")).hexdigest()[:32]
        title = document.title or self._extract_title(text) or document.url
        self.store.upsert_node(KnowledgeNode(
            id=node_id, type=NodeType.SOURCE, title=title,
            description="Imported public web document", status="active", confidence=0.9,
            properties={"kind": "web_document", "sha256": digest, "content_type": content_type},
            evidence=[Evidence(source_id=node_id, url=document.url, quote=text[:4000],
                               version=document.version, confidence=0.9,
                               metadata={"bytes": len(raw)})],
        ))
        return 1

    @staticmethod
    def _html_to_text(html: str) -> str:
        html = re.sub(r"(?is)<(script|style|noscript|svg).*?>.*?</\1>", " ", html)
        html = re.sub(r"(?is)<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", unescape(html)).strip()

    @staticmethod
    def _extract_title(text: str) -> str | None:
        return text[:160].strip() or None

"""Deterministic normalization and lightweight entity/relation extraction.

This layer converts imported evidence into conservative graph facts. It never
promotes a claim to a confirmed bug solely from keywords: extracted BUG/GLITCH/
ANOMALY nodes start as ``suspected`` and retain their source evidence.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

from .models import Edge, Evidence, KnowledgeNode, NodeType
from .store import KnowledgeStore


@dataclass(frozen=True)
class ExtractedFact:
    node: KnowledgeNode
    relation: str | None = None
    target_id: str | None = None


class KnowledgeNormalizer:
    BUG_PATTERNS = (
        r"\bbug(?:s)?\b", r"\bglitch(?:es)?\b", r"\bexploit(?:s)?\b",
        r"\banomal(?:y|ies)\b", r"\berror(?:s)?\b", r"\bcrash(?:es|ing)?\b",
        r"\bfix(?:ed|es)?\b", r"\bissue(?:s)?\b",
    )
    PACKET_RE = re.compile(r"\b(?:packet|header)\s*[:#-]?\s*([a-z][a-z0-9_]{1,40})\b", re.I)
    VERSION_RE = re.compile(r"\b(?:v|version|ver\.?|patch)\s*([0-9]+(?:\.[0-9]+){1,3})\b", re.I)

    def __init__(self, store: KnowledgeStore) -> None:
        self.store = store

    @staticmethod
    def _id(prefix: str, value: str) -> str:
        digest = hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()[:24]
        return f"{prefix}:{digest}"

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def normalize_source(self, source: KnowledgeNode, evidence: Iterable[Evidence] | None = None) -> list[KnowledgeNode]:
        """Extract conservative entities from source evidence and connect them."""
        evidences = list(evidence or source.evidence)
        created: list[KnowledgeNode] = []
        for ev in evidences:
            text = self._clean(ev.quote or "")
            if not text:
                continue
            for node in self._extract_entities(text, ev):
                self.store.upsert_node(node)
                self.store.upsert_edge(Edge(
                    id=self._id("edge", f"{source.id}|SUPPORTED_BY|{node.id}"),
                    source_id=node.id, relation="SUPPORTED_BY", target_id=source.id,
                    confidence=min(node.confidence, ev.confidence),
                ))
                created.append(node)
        return created

    def _extract_entities(self, text: str, ev: Evidence) -> list[KnowledgeNode]:
        facts: list[KnowledgeNode] = []
        lower = text.lower()
        bug_hits = [p for p in self.BUG_PATTERNS if re.search(p, text, re.I)]
        if bug_hits:
            title = self._sentence(text)
            node_id = self._id("anomaly", title)
            kind = NodeType.BUG if any(x in lower for x in ("bug", "issue", "fix")) else NodeType.ANOMALY
            facts.append(KnowledgeNode(
                id=node_id, type=kind, title=title[:180],
                description="Extracted claim requiring verification", status="suspected",
                confidence=min(0.65, max(0.2, ev.confidence * 0.65)),
                properties={"extraction": "keyword", "matched_terms": bug_hits},
                evidence=[Evidence(source_id=ev.source_id, url=ev.url, quote=text[:2000],
                                    version=ev.version, confidence=ev.confidence, metadata=ev.metadata)],
            ))

        for match in self.PACKET_RE.finditer(text):
            name = match.group(1).lower()
            facts.append(KnowledgeNode(
                id=self._id("packet", name), type=NodeType.PACKET, title=name,
                description="Packet identifier extracted from source evidence", status="observed",
                confidence=min(0.9, ev.confidence), properties={"extraction": "pattern"},
                evidence=[Evidence(source_id=ev.source_id, url=ev.url, quote=text[:1000],
                                    version=ev.version, confidence=ev.confidence, metadata=ev.metadata)],
            ))

        for match in self.VERSION_RE.finditer(text):
            version = match.group(1)
            facts.append(KnowledgeNode(
                id=self._id("version", version), type=NodeType.VERSION, title=version,
                description="Version identifier extracted from source evidence", status="observed",
                confidence=min(0.95, ev.confidence), properties={"extraction": "pattern"},
                evidence=[Evidence(source_id=ev.source_id, url=ev.url, quote=text[:1000],
                                    version=version, confidence=ev.confidence, metadata=ev.metadata)],
            ))
        return facts

    @staticmethod
    def _sentence(text: str) -> str:
        parts = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)
        return parts[0] if parts else text

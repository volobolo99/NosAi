"""Normalize verified NosCore schema documents into knowledge candidates."""
from __future__ import annotations

from typing import Any, Mapping

from .source_adapters import KnowledgeCandidate


def packet_schema_candidates(
    schemas: Mapping[str, Mapping[str, Any]],
    *,
    source_ref: str,
    source_commit: str | None = None,
) -> list[KnowledgeCandidate]:
    """Convert a schema mapping into candidates without inventing semantics.

    The adapter records the declared schema verbatim under ``fields``. It does
    not infer canonical game meaning from field names. Semantic promotion is a
    separate verification step.
    """
    result: list[KnowledgeCandidate] = []
    for packet_name, schema in schemas.items():
        if not packet_name or not isinstance(schema, Mapping):
            raise ValueError("packet name and schema mapping are required")
        result.append(
            KnowledgeCandidate(
                record_id=packet_name,
                kind="packet_schema",
                fields=dict(schema),
                source_id="noscore.packets",
                source_ref=source_ref,
                source_commit=source_commit,
            )
        )
    return result

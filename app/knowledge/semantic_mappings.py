"""Explicit semantic mappings kept separate from raw packet schemas."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class SemanticMapping:
    packet: str
    source_field: str
    canonical_field: str
    transform: str = "identity"
    evidence: str = ""
    verified: bool = False


def apply_mapping(fields: Mapping[str, Any], mapping: SemanticMapping) -> dict[str, Any]:
    if mapping.source_field not in fields:
        return {}
    return {mapping.canonical_field: fields[mapping.source_field]}


# Only mappings with explicit evidence should be marked verified. The initial
# catalog contains headers whose field semantics still require schema/capture.
INITIAL_MAPPINGS: tuple[SemanticMapping, ...] = ()

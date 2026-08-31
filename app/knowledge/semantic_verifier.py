"""Verify semantic mapping candidates against declared packet schemas.

This verifier checks structural evidence only. It deliberately does not claim
that a field's game meaning is correct merely because the field exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Iterable


@dataclass(frozen=True)
class VerificationResult:
    packet: str
    source_field: str
    canonical_field: str
    schema_present: bool
    type_matches: bool | None
    verified: bool
    reason: str


def verify_candidate(candidate: Mapping[str, Any], schema: Mapping[str, Any]) -> VerificationResult:
    packet = str(candidate.get("packet", ""))
    source_field = str(candidate.get("source_field", ""))
    canonical_field = str(candidate.get("canonical_field", ""))
    fields = schema.get("fields", [])
    if not isinstance(fields, Iterable) or isinstance(fields, (str, bytes)):
        return VerificationResult(packet, source_field, canonical_field, False, None, False, "schema has no field list")
    found = None
    for field in fields:
        if isinstance(field, Mapping) and field.get("name") == source_field:
            found = field
            break
    if found is None:
        return VerificationResult(packet, source_field, canonical_field, False, None, False, "source field absent from schema")
    # Structural presence is evidence, not semantic proof.
    return VerificationResult(packet, source_field, canonical_field, True, None, False, "field present; semantic meaning requires independent evidence")

"""Deterministic append-only store for promoted knowledge records."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .source_adapters import KnowledgeCandidate


def write_promoted_records(path: str | Path, records: Iterable[KnowledgeCandidate]) -> int:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with target.open("w", encoding="utf-8") as handle:
        for record in sorted(records, key=lambda item: (item.kind, item.record_id, item.source_id)):
            handle.write(json.dumps({
                "record_id": record.record_id,
                "kind": record.kind,
                "fields": dict(record.fields),
                "source_id": record.source_id,
                "source_ref": record.source_ref,
                "source_version": record.source_version,
                "source_commit": record.source_commit,
            }, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count

"""Canonical representation and validation for NosAi datasets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


class DatasetValidationError(ValueError):
    """Raised when source data cannot be represented safely."""


@dataclass(frozen=True)
class CanonicalRecord:
    """Stable record envelope independent of the upstream provider format."""

    dataset: str
    record_id: str
    attributes: Mapping[str, Any]
    source: str | None = None
    source_version: str | None = None


@dataclass
class CanonicalDataset:
    """Validated dataset ready for indexing and World Model ingestion."""

    name: str
    schema_version: int
    records: list[CanonicalRecord] = field(default_factory=list)

    def ids(self) -> set[str]:
        return {record.record_id for record in self.records}


class DatasetNormalizer:
    """Normalize common mapping/list API responses into canonical records."""

    def normalize(
        self,
        dataset: str,
        payload: Any,
        *,
        schema_version: int = 1,
        source: str | None = None,
        source_version: str | None = None,
    ) -> CanonicalDataset:
        if not dataset.strip():
            raise DatasetValidationError("dataset name cannot be empty")
        if not isinstance(payload, (list, tuple, dict)):
            raise DatasetValidationError(f"unsupported payload for '{dataset}'")

        items: list[tuple[str, Mapping[str, Any]]] = []
        if isinstance(payload, dict):
            for key, value in payload.items():
                if not isinstance(value, Mapping):
                    raise DatasetValidationError(
                        f"record '{key}' in '{dataset}' must be an object"
                    )
                items.append((str(key), value))
        else:
            for index, value in enumerate(payload):
                if not isinstance(value, Mapping):
                    raise DatasetValidationError(
                        f"record at index {index} in '{dataset}' must be an object"
                    )
                record_id = value.get("id", value.get("ID"))
                if record_id is None:
                    raise DatasetValidationError(
                        f"record at index {index} in '{dataset}' has no id"
                    )
                items.append((str(record_id), value))

        records = [
            CanonicalRecord(
                dataset=dataset,
                record_id=record_id,
                attributes=dict(attributes),
                source=source,
                source_version=source_version,
            )
            for record_id, attributes in items
        ]
        ids = [record.record_id for record in records]
        if len(ids) != len(set(ids)):
            raise DatasetValidationError(f"duplicate record id in '{dataset}'")
        return CanonicalDataset(dataset, schema_version, records)


def validate_references(
    dataset: CanonicalDataset,
    references: Mapping[str, set[str]],
) -> list[str]:
    """Return missing referenced IDs without mutating the source dataset."""
    missing: list[str] = []
    for field_name, valid_ids in references.items():
        for record in dataset.records:
            value = record.attributes.get(field_name)
            if value is None:
                continue
            values = value if isinstance(value, (list, tuple, set)) else [value]
            for referenced_id in values:
                if str(referenced_id) not in valid_ids:
                    missing.append(
                        f"{dataset.name}:{record.record_id}:{field_name}={referenced_id}"
                    )
    return missing

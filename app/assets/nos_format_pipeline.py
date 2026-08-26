"""Normalized NosTale format pipeline boundary.

The concrete .NOS/NSpn/NSpc/NSpm parsing implementation can be supplied by a
Taletool adapter or a native parser. Keeping this boundary explicit prevents
binary-format assumptions from leaking into the renderer.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .asset_registry import AssetRegistry


@dataclass(frozen=True)
class ParsedAssetSet:
    source_root: Path
    registry: AssetRegistry
    parser: str


class NosAssetParser(Protocol):
    name: str

    def parse(self, root: Path) -> ParsedAssetSet: ...


def parse_with(parser: NosAssetParser, root: str | Path) -> ParsedAssetSet:
    source_root = Path(root).resolve()
    if not source_root.is_dir():
        raise NotADirectoryError(source_root)
    result = parser.parse(source_root)
    if result.source_root != source_root:
        raise ValueError("il parser deve restituire la root sorgente normalizzata")
    return result

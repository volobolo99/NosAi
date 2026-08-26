"""Persistent, dependency-free item catalog for dashboard observations."""
from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .nosapki import ItemMetadata, fetch_item


@dataclass(frozen=True)
class CatalogItem:
    item_id: str
    nome: str | None
    immagine_url: str | None
    fonte_url: str


class ItemCatalog:
    """SQLite cache that enriches encountered items without requiring credentials."""

    def __init__(self, path: str | Path = "data/nosai_items.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS items ("
                "item_id TEXT PRIMARY KEY, nome TEXT, immagine_url TEXT, fonte_url TEXT NOT NULL)"
            )

    def upsert(self, item: CatalogItem) -> CatalogItem:
        with sqlite3.connect(self.path) as db:
            db.execute(
                "INSERT INTO items(item_id,nome,immagine_url,fonte_url) VALUES(?,?,?,?) "
                "ON CONFLICT(item_id) DO UPDATE SET nome=excluded.nome, "
                "immagine_url=excluded.immagine_url, fonte_url=excluded.fonte_url",
                (item.item_id, item.nome, item.immagine_url, item.fonte_url),
            )
        return item

    def get(self, item_id: str) -> CatalogItem | None:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT item_id,nome,immagine_url,fonte_url FROM items WHERE item_id=?", (item_id,)
            ).fetchone()
        return CatalogItem(*row) if row else None

    def enrich_observed(self, data: dict[str, Any]) -> CatalogItem | None:
        """Enrich one observed item when the runtime provides a NosApki source URL."""
        item_id = str(data.get("id") or data.get("item_id") or "").strip()
        source_url = str(data.get("fonte_url") or data.get("source_url") or "").strip()
        if not item_id or not source_url:
            return None
        metadata: ItemMetadata = fetch_item(source_url)
        return self.upsert(
            CatalogItem(item_id, metadata.nome or data.get("nome"), metadata.immagine_url, metadata.fonte_url)
        )

    def as_dict(self, item: CatalogItem) -> dict[str, Any]:
        return asdict(item)

from pathlib import Path

from app.dashboard.catalog import CatalogItem, ItemCatalog


def test_item_catalog_persists_and_reads_items(tmp_path: Path) -> None:
    catalog = ItemCatalog(tmp_path / "items.sqlite3")
    item = CatalogItem("gemma-1", "Gemma", "https://nosapki.com/image.png", "https://nosapki.com/it/items/gemma")
    catalog.upsert(item)
    assert catalog.get("gemma-1") == item


def test_item_catalog_enriches_observed_item(tmp_path: Path, monkeypatch) -> None:
    from app.dashboard import catalog as module
    from app.dashboard.nosapki import ItemMetadata

    catalog = ItemCatalog(tmp_path / "items.sqlite3")
    monkeypatch.setattr(
        module,
        "fetch_item",
        lambda url: ItemMetadata("Gemma", "https://nosapki.com/image.png", url),
    )
    item = catalog.enrich_observed({"id": "gemma-1", "fonte_url": "https://nosapki.com/it/items/gemma"})
    assert item is not None
    assert item.nome == "Gemma"
    assert item.immagine_url == "https://nosapki.com/image.png"
    assert catalog.get("gemma-1") == item


def test_item_catalog_preserves_existing_metadata_on_partial_update(tmp_path: Path) -> None:
    catalog = ItemCatalog(tmp_path / "items.sqlite3")
    original = CatalogItem(
        "gemma-1",
        "Gemma",
        "https://nosapki.com/image.png",
        "https://nosapki.com/it/items/gemma",
    )
    catalog.upsert(original)

    updated = catalog.upsert(
        CatalogItem("gemma-1", None, None, "https://nosapki.com/it/items/gemma?v=2")
    )

    assert updated.item_id == original.item_id
    assert updated.nome == original.nome
    assert updated.immagine_url == original.immagine_url
    assert updated.fonte_url.endswith("v=2")

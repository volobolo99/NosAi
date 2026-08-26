"""External data-source registry used by the dashboard.

URLs are configuration/data references only. External services are queried by the
backend when a supported connector is implemented; browser code never receives
secrets.
"""

from __future__ import annotations

NOSAPKI_SOURCES = {
    "oggetti_vendita": "https://nosapki.com/it/items/sales",
    "materiali": "https://nosapki.com/it/items/material",
    "altri_oggetti": "https://nosapki.com/it/items/other",
    "oggetti_speciali": "https://nosapki.com/it/items/special_items",
}

OFFICIAL_SOURCES = {
    "openai_api_docs": "https://platform.openai.com/docs",
    "github_api_docs": "https://docs.github.com/en/rest",
}


def image_reference(item: dict[str, object]) -> str | None:
    """Return a trusted image URL already supplied by a data adapter.

    We deliberately do not scrape or invent an image URL from an item name.
    A future NosApki connector can populate ``image_url`` after validating it.
    """

    value = item.get("image_url")
    return value if isinstance(value, str) and value.startswith(("https://", "http://")) else None


def all_sources() -> dict[str, str]:
    return {**NOSAPKI_SOURCES, **OFFICIAL_SOURCES}

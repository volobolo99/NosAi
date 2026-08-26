"""Small, dependency-light NosApki HTML connector for item metadata.

The connector only reads public pages supplied by the configured source. It
never embeds credentials and never fabricates an image URL.
"""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Callable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

NOSAPKI_HOST = "nosapki.com"


@dataclass(frozen=True)
class ItemMetadata:
    nome: str | None
    immagine_url: str | None
    fonte_url: str


class _MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {k.lower(): v for k, v in attrs}
        if tag.lower() == "meta":
            key = values.get("property") or values.get("name")
            content = values.get("content")
            if key and content:
                self.meta[key.lower()] = content
        elif tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data.strip())


def _trusted_http_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname == NOSAPKI_HOST


def parse_item_html(html: str, source_url: str) -> ItemMetadata:
    parser = _MetaParser()
    parser.feed(html)
    image = parser.meta.get("og:image")
    image_url = urljoin(source_url, image) if image else None
    if image_url and not _trusted_http_url(image_url):
        image_url = None
    name = parser.meta.get("og:title") or (parser.title_parts[0] if parser.title_parts else None)
    return ItemMetadata(nome=name, immagine_url=image_url, fonte_url=source_url)


def fetch_item(url: str, opener: Callable[..., object] | None = None, timeout: float = 8.0) -> ItemMetadata:
    """Fetch one NosApki item page and extract safe metadata."""
    if not _trusted_http_url(url):
        raise ValueError("Sono consentite solo pagine HTTPS di nosapki.com")
    request = Request(url, headers={"User-Agent": "NosAi/1.0 (observability connector)"})
    open_fn = opener or urlopen
    response = open_fn(request, timeout=timeout)
    html = response.read().decode("utf-8", errors="replace")
    return parse_item_html(html, url)

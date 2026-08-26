"""Controlled GitHub/Web research crawler.

The crawler is intentionally bounded and allowlisted. It gathers public source
material, stores provenance, and immediately normalizes evidence into the graph.
It never executes repository code and never follows external domains.
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html import unescape

from .graph_builder import KnowledgeGraphBuilder
from .importers.github import GitHubImporter, GitHubRepository
from .importers.web import WebDocument, WebImporter
from .models import KnowledgeNode
from .store import KnowledgeStore


@dataclass(frozen=True)
class CrawlLimits:
    max_github_files: int = 80
    max_github_depth: int = 4
    max_web_pages: int = 12
    max_web_bytes: int = 1_000_000


class ResearchCrawler:
    TEXT_EXTENSIONS = {
        ".md", ".txt", ".json", ".yaml", ".yml", ".xml", ".csv", ".cs", ".py",
        ".java", ".js", ".ts", ".cpp", ".h", ".hpp", ".ini", ".cfg", ".toml",
    }

    def __init__(self, store: KnowledgeStore, limits: CrawlLimits | None = None) -> None:
        self.store = store
        self.limits = limits or CrawlLimits()
        self.github = GitHubImporter(store)
        self.web = WebImporter(store, max_bytes=self.limits.max_web_bytes)
        self.graph = KnowledgeGraphBuilder(store)

    def crawl_github(self, repo: GitHubRepository) -> int:
        """Walk a bounded public repository and import text source files."""
        queue: list[tuple[str, int]] = [("", 0)]
        visited: set[str] = set()
        imported = 0
        while queue and imported < self.limits.max_github_files:
            path, depth = queue.pop(0)
            if path in visited or depth > self.limits.max_github_depth:
                continue
            visited.add(path)
            url = (
                f"https://api.github.com/repos/{repo.owner}/{repo.name}/contents/"
                f"{urllib.parse.quote(path)}?ref={urllib.parse.quote(repo.ref)}"
            )
            payload = self.github._get(url)
            entries = payload if isinstance(payload, list) else [payload]
            for entry in entries:
                if imported >= self.limits.max_github_files:
                    break
                entry_path = entry.get("path", "")
                if entry.get("type") == "dir":
                    queue.append((entry_path, depth + 1))
                elif entry.get("type") == "file" and self._is_text_file(entry_path):
                    imported += self.github.import_file(repo, entry_path)
        return imported

    def crawl_web(self, start_url: str) -> int:
        """Follow same-domain HTML links up to the configured page limit."""
        parsed = urllib.parse.urlparse(start_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("start_url must be an absolute http(s) URL")
        host = parsed.netloc.lower()
        queue = [start_url]
        visited: set[str] = set()
        imported = 0
        while queue and imported < self.limits.max_web_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            request = urllib.request.Request(url, headers={"User-Agent": "NosAi-ResearchCrawler/1.0"})
            try:
                with urllib.request.urlopen(request, timeout=self.web.timeout) as response:
                    if response.headers.get_content_type() != "text/html":
                        continue
                    raw = response.read(self.limits.max_web_bytes + 1)
                    if len(raw) > self.limits.max_web_bytes:
                        continue
                    html = raw.decode("utf-8", errors="replace")
            except Exception:
                continue
            title = self._title(html)
            self.web.import_document(WebDocument(url=url, title=title))
            imported += 1
            for href in re.findall(r"(?is)href=[\"']([^\"']+)[\"']", html):
                child = urllib.parse.urljoin(url, unescape(href)).split("#", 1)[0]
                child_parsed = urllib.parse.urlparse(child)
                if child_parsed.scheme in {"http", "https"} and child_parsed.netloc.lower() == host:
                    if child not in visited and child not in queue:
                        queue.append(child)
        return imported

    @staticmethod
    def _is_text_file(path: str) -> bool:
        lower = path.lower()
        return any(lower.endswith(ext) for ext in ResearchCrawler.TEXT_EXTENSIONS)

    @staticmethod
    def _title(html: str) -> str | None:
        match = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
        if not match:
            return None
        return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", match.group(1)))).strip()[:200]

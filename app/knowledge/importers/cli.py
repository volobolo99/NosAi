"""CLI entry point for controlled knowledge ingestion."""
from __future__ import annotations

import argparse

from ..store import KnowledgeStore
from .github import GitHubImporter, GitHubRepository
from .web import WebDocument, WebImporter


def main() -> int:
    parser = argparse.ArgumentParser(description="NosAi knowledge source importer")
    parser.add_argument("--db", default="data/knowledge/nosai_knowledge.sqlite3")
    sub = parser.add_subparsers(dest="command", required=True)

    gh = sub.add_parser("github", help="import public GitHub repository metadata/files")
    gh.add_argument("repo", help="owner/name")
    gh.add_argument("--ref", default="main")
    gh.add_argument("--path", action="append", default=[])
    web = sub.add_parser("web", help="import one public HTML/text document")
    web.add_argument("url")
    web.add_argument("--title")
    web.add_argument("--version")

    args = parser.parse_args()
    store = KnowledgeStore(args.db)
    if args.command == "github":
        owner, name = args.repo.split("/", 1)
        count = GitHubImporter(store).import_repository(GitHubRepository(owner, name, args.ref), tuple(args.path))
    else:
        count = WebImporter(store).import_document(WebDocument(args.url, args.title, args.version))
    print(f"Imported {count} knowledge source record(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

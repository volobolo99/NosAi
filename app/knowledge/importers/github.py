"""Read-only GitHub importer for public repositories.

The importer stores repository metadata and selected text files as SOURCE nodes.
It never executes downloaded code and intentionally uses only the Python stdlib.
"""
from __future__ import annotations

import base64
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from ..models import Evidence, KnowledgeNode, NodeType
from ..store import KnowledgeStore


@dataclass(frozen=True)
class GitHubRepository:
    owner: str
    name: str
    ref: str = "main"


class GitHubImporter:
    def __init__(self, store: KnowledgeStore, token: str | None = None, timeout: int = 20) -> None:
        self.store = store
        self.token = token
        self.timeout = timeout

    def _get(self, url: str) -> Any:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "NosAi-KnowledgeImporter/1.0"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def import_repository(self, repo: GitHubRepository, paths: tuple[str, ...] = ()) -> int:
        api = f"https://api.github.com/repos/{urllib.parse.quote(repo.owner)}/{urllib.parse.quote(repo.name)}"
        metadata = self._get(api)
        source_id = f"github:{repo.owner}/{repo.name}"
        self.store.upsert_node(KnowledgeNode(
            id=source_id, type=NodeType.SOURCE,
            title=metadata.get("full_name", f"{repo.owner}/{repo.name}"),
            description=metadata.get("description") or "Public GitHub repository",
            status="active", confidence=1.0,
            properties={"kind": "github_repository", "default_branch": metadata.get("default_branch")},
            evidence=[Evidence(source_id=source_id, url=metadata.get("html_url"),
                               quote="Repository metadata", confidence=1.0)],
        ))
        count = 1
        for path in paths:
            count += self.import_file(repo, path)
        return count

    def import_file(self, repo: GitHubRepository, path: str) -> int:
        encoded_path = "/".join(urllib.parse.quote(part) for part in path.split("/"))
        url = f"https://api.github.com/repos/{repo.owner}/{repo.name}/contents/{encoded_path}?ref={urllib.parse.quote(repo.ref)}"
        payload = self._get(url)
        if payload.get("type") != "file" or payload.get("encoding") != "base64":
            return 0
        raw = base64.b64decode(payload["content"])
        digest = sha256(raw).hexdigest()
        node_id = f"github-file:{repo.owner}/{repo.name}:{repo.ref}:{path}"
        text = raw.decode("utf-8", errors="replace")
        self.store.upsert_node(KnowledgeNode(
            id=node_id, type=NodeType.SOURCE, title=path,
            description=f"GitHub source file ({len(raw)} bytes)", status="active", confidence=1.0,
            properties={"kind": "github_file", "sha256": digest, "repository": f"{repo.owner}/{repo.name}", "ref": repo.ref},
            evidence=[Evidence(source_id=node_id, url=payload.get("html_url"),
                               quote=text[:2000], version=repo.ref, confidence=1.0,
                               metadata={"blob_sha": payload.get("sha")})],
        ))
        return 1

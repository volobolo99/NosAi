"""Extract a clean benchmark corpus from Git history without executing code."""
from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Sequence

from .bug_corpus import BugCorpusExample, build_bug_example, build_corpus


@dataclass(frozen=True, slots=True)
class GitCommitEvidence:
    commit: str
    subject: str
    body: str
    patch: str


def collect_git_history(repository: str, *, limit: int = 50) -> Sequence[GitCommitEvidence]:
    """Collect commit metadata and patches; repository code is never executed."""
    if limit <= 0:
        return ()
    result = subprocess.run(
        ["git", "-C", repository, "log", f"-{limit}", "--format=%H%x1f%s%x1f%b%x1e", "--patch"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git history collection failed")

    records: list[GitCommitEvidence] = []
    for block in result.stdout.split("\x1e"):
        header, separator, patch = block.partition("\n")
        if not separator:
            continue
        parts = header.split("\x1f")
        if len(parts) < 3 or not parts[0].strip():
            continue
        records.append(GitCommitEvidence(parts[0].strip(), parts[1].strip(), parts[2].strip(), patch))
    return records


def build_history_corpus(
    repository: str,
    *,
    repository_id: str,
    project_id: str,
    limit: int = 50,
) -> tuple[BugCorpusExample, ...]:
    """Build candidate examples; only explicitly bug/fix-like commits become corpus rows."""
    examples: list[BugCorpusExample] = []
    for item in collect_git_history(repository, limit=limit):
        subject = item.subject.lower()
        if not any(word in subject for word in ("fix", "bug", "error", "crash", "test", "regression")):
            continue
        examples.append(
            build_bug_example(
                example_id=f"git-{item.commit}",
                repository_id=repository_id,
                project_id=project_id,
                error_signature=item.subject,
                stack_trace=item.body,
                root_cause=item.body,
                patch_summary=item.patch[:12000],
                lesson=item.subject,
            )
        )
    return build_corpus(examples)

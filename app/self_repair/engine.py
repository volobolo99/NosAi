"""Conservative autonomous repair orchestration.

A resolver supplies hypotheses; this module never executes arbitrary model output.
Only structured file operations under the workspace allowlist can be applied, and
only after validation demonstrates a measurable improvement.
"""

from __future__ import annotations

import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from .journal import RepairJournal
from .models import ErrorEvent, RepairCandidate, RepairResult, ValidationResult
from .workspace import RepairWorkspace, WorkspacePolicyError

CandidateResolver = Callable[[ErrorEvent, RepairWorkspace], Sequence[RepairCandidate]]


@dataclass(frozen=True)
class RepairPolicy:
    min_confidence: float = 0.80
    min_score: float = 0.20
    min_validation_score: float = 0.80
    max_risk: float = 0.35
    allow_delete: bool = False
    allow_main_workspace: bool = True
    test_command: tuple[str, ...] = ("python", "-m", "pytest", "-q")


class RepairEngine:
    def __init__(self, root: str | Path, journal: RepairJournal, policy: RepairPolicy | None = None) -> None:
        self.root = Path(root).resolve()
        self.policy = policy or RepairPolicy()
        self.workspace = RepairWorkspace(self.root)
        self.journal = journal

    def handle_error(self, event: ErrorEvent, resolver: CandidateResolver) -> RepairResult:
        self.journal.record("error", event)
        candidates = [c for c in resolver(event, self.workspace) if self._eligible(c)]
        candidates.sort(key=lambda c: c.score, reverse=True)
        if not candidates:
            result = RepairResult(event.error_id, "BLOCKED", None, None, "no candidate met the repair policy")
            self.journal.record("repair_result", result)
            return result

        candidate = candidates[0]
        self.journal.record("candidate", candidate)
        run_id = f"{event.error_id}-{uuid.uuid4().hex[:10]}"
        try:
            if any(op.operation == "delete" for op in candidate.operations) and not self.policy.allow_delete:
                raise WorkspacePolicyError("delete operations are disabled by policy")
            self.workspace.apply(candidate.operations, run_id)
            validation = self._validate()
        except (OSError, WorkspacePolicyError, subprocess.SubprocessError) as exc:
            result = RepairResult(event.error_id, "FAILED", candidate.candidate_id, None, f"repair failed: {type(exc).__name__}: {exc}")
            self.journal.record("repair_result", result)
            return result

        if not validation.passed or validation.score < self.policy.min_validation_score:
            result = RepairResult(event.error_id, "REJECTED", candidate.candidate_id, validation, "validation did not prove sufficient improvement")
        else:
            result = RepairResult(event.error_id, "APPLIED", candidate.candidate_id, validation, "candidate applied and validation passed")
        self.journal.record("repair_result", result)
        return result

    def _eligible(self, candidate: RepairCandidate) -> bool:
        return (
            candidate.confidence >= self.policy.min_confidence
            and candidate.risk <= self.policy.max_risk
            and candidate.score >= self.policy.min_score
            and (self.policy.allow_main_workspace or self.root.name != "main")
        )

    def _validate(self) -> ValidationResult:
        try:
            completed = subprocess.run(
                self.policy.test_command,
                cwd=self.root,
                text=True,
                capture_output=True,
                timeout=300,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return ValidationResult(False, 0.0, 0, 0, f"validation infrastructure error: {type(exc).__name__}: {exc}")
        passed = completed.returncode == 0
        return ValidationResult(passed, 1.0 if passed else 0.0, 1 if passed else 0, 0 if passed else 1, completed.stdout + completed.stderr)

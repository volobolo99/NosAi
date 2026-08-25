"""Conservative autonomous repair orchestration.

A resolver supplies hypotheses; this module never executes arbitrary model output.
Only structured file operations under the workspace allowlist can be applied, and
only after strict validation demonstrates a measurable improvement.
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
    """Maximum-severity repair policy.

    A repair is accepted only when every local quality gate passes. Remote
    CodeQL/SonarCloud gates are enforced by CI before the change is considered
    releasable; they are deliberately not faked as local checks.
    """

    min_confidence: float = 0.95
    min_score: float = 0.50
    min_validation_score: float = 1.0
    max_risk: float = 0.10
    allow_delete: bool = False
    allow_main_workspace: bool = True
    test_commands: tuple[tuple[str, ...], ...] = (
        ("python", "-m", "compileall", "-q", "app", "tests"),
        ("ruff", "check", "app", "tests"),
        ("python", "-m", "pytest", "-q"),
    )


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
            result = RepairResult(event.error_id, "BLOCKED", None, None, "no candidate met the maximum-severity repair policy")
            self.journal.record("repair_result", result)
            return result

        candidate = candidates[0]
        self.journal.record("candidate", candidate)
        run_id = f"{event.error_id}-{uuid.uuid4().hex[:10]}"
        mutated = False
        try:
            if any(op.operation == "delete" for op in candidate.operations) and not self.policy.allow_delete:
                raise WorkspacePolicyError("delete operations are disabled by maximum-severity policy")
            self.workspace.apply(candidate.operations, run_id)
            mutated = True
            validation = self._validate()
        except (OSError, WorkspacePolicyError, subprocess.SubprocessError) as exc:
            if mutated:
                self.workspace.rollback(candidate.operations, run_id)
            result = RepairResult(event.error_id, "FAILED", candidate.candidate_id, None, f"repair failed: {type(exc).__name__}: {exc}")
            self.journal.record("repair_result", result)
            return result

        if not validation.passed or validation.score < self.policy.min_validation_score:
            self.workspace.rollback(candidate.operations, run_id)
            result = RepairResult(event.error_id, "REJECTED", candidate.candidate_id, validation, "strict validation did not prove the repair; changes rolled back")
        else:
            result = RepairResult(event.error_id, "APPLIED", candidate.candidate_id, validation, "all local quality gates passed")
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
        outputs: list[str] = []
        passed_count = 0
        try:
            for command in self.policy.test_commands:
                completed = subprocess.run(
                    command,
                    cwd=self.root,
                    text=True,
                    capture_output=True,
                    timeout=300,
                    check=False,
                )
                output = completed.stdout + completed.stderr
                outputs.append(f"$ {' '.join(command)}\n{output}")
                if completed.returncode != 0:
                    return ValidationResult(False, 0.0, passed_count, len(self.policy.test_commands) - passed_count, "\n".join(outputs))
                passed_count += 1
        except (OSError, subprocess.SubprocessError) as exc:
            return ValidationResult(False, 0.0, passed_count, len(self.policy.test_commands) - passed_count, f"validation infrastructure error: {type(exc).__name__}: {exc}\n" + "\n".join(outputs))
        return ValidationResult(True, 1.0, passed_count, 0, "\n".join(outputs))

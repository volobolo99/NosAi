"""Persistent verification metadata for autonomous skills."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SkillRecord:
    name: str
    version: str
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    confidence: float = 0.0
    verified: bool = False
    dependencies: tuple[str, ...] = ()

    @property
    def success_rate(self) -> float:
        return self.successes / self.attempts if self.attempts else 0.0

    def record(self, success: bool, confidence: float, verification_threshold: float = 0.8) -> None:
        self.attempts += 1
        if success:
            self.successes += 1
        else:
            self.failures += 1
        self.confidence = max(0.0, min(1.0, confidence))
        self.verified = self.attempts >= 3 and self.success_rate >= verification_threshold and self.confidence >= verification_threshold


@dataclass
class SkillLedger:
    skills: dict[str, SkillRecord] = field(default_factory=dict)

    def upsert(self, record: SkillRecord) -> None:
        self.skills[record.name] = record

    def record_result(self, name: str, success: bool, confidence: float) -> SkillRecord:
        record = self.skills[name]
        record.record(success, confidence)
        return record

from __future__ import annotations

from dataclasses import dataclass

from .contracts import Action


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()


def validate_action(action: Action) -> ValidationResult:
    errors: list[str] = []
    if not action.action_id:
        errors.append("action_id is required")
    if not action.schema_version:
        errors.append("schema_version is required")
    if not action.action_type:
        errors.append("action_type is required")
    if not isinstance(action.parameters, dict):
        errors.append("parameters must be a mapping")
    return ValidationResult(valid=not errors, errors=tuple(errors))

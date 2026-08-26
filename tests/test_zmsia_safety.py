from app.zmsia.core.contracts import Action
from app.zmsia.core.safety import DefaultSafetyPolicy
from app.zmsia.core.validation import validate_action


def action(action_type: str = "noop") -> Action:
    """Build a canonical ZMSIA action for safety tests."""
    return Action(
        schema_version=1,
        action_id="test-action",
        action_type=action_type,
        parameters={},
    )


def test_validation_accepts_well_formed_action():
    """A complete action should pass structural validation."""
    result = validate_action(action())
    assert result.valid
    assert result.errors == ()


def test_validation_rejects_missing_action_type():
    """An action without an explicit type must be rejected."""
    result = validate_action(Action(schema_version=1, action_id="x", action_type="", parameters={}))
    assert not result.valid
    assert "action_type is required" in result.errors


def test_safety_is_deny_by_default_for_unknown_action():
    """Unknown action types must be rejected by the default policy."""
    result = DefaultSafetyPolicy().validate(action("client_move"))
    assert not result.allowed


def test_safety_allows_only_noop_in_dry_run():
    """Only noop is allowed by the conservative dry-run policy."""
    result = DefaultSafetyPolicy().validate(action("noop"))
    assert result.allowed

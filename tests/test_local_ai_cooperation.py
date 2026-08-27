from nosai.local_ai.cooperation import (
    AIProposal,
    CooperationMode,
    CooperationPolicy,
    CooperationRequest,
    DecisionRole,
)


def proposal(source, action, confidence):
    return AIProposal(source=source, action=action, confidence=confidence)


def test_primary_remains_authoritative_for_local_assist():
    policy = CooperationPolicy()
    request = CooperationRequest(task="combat", context={}, risk_level=0.2)
    decision = policy.arbitrate(
        request,
        proposal(DecisionRole.PRIMARY, "attack", 0.9),
        proposal(DecisionRole.SECONDARY, "defend", 0.8),
        local_ready=True,
    )
    assert decision.mode is CooperationMode.LOCAL_ASSIST
    assert decision.selected is DecisionRole.PRIMARY
    assert decision.action == "attack"


def test_high_risk_matching_proposals_reach_consensus():
    policy = CooperationPolicy()
    request = CooperationRequest(task="critical", context={}, risk_level=0.9)
    decision = policy.arbitrate(
        request,
        proposal(DecisionRole.PRIMARY, "retreat", 0.9),
        proposal(DecisionRole.SECONDARY, "retreat", 0.85),
        local_ready=True,
    )
    assert decision.mode is CooperationMode.DUAL_REVIEW
    assert decision.selected is DecisionRole.CONSENSUS


def test_local_unavailable_does_not_block_primary():
    policy = CooperationPolicy()
    request = CooperationRequest(task="combat", context={})
    decision = policy.arbitrate(
        request,
        proposal(DecisionRole.PRIMARY, "attack", 0.8),
        None,
        local_ready=False,
    )
    assert decision.mode is CooperationMode.PRIMARY_ONLY
    assert decision.action == "attack"

from tools.validate_reference_templates import validate


def test_public_reference_cannot_be_production_template():
    errors = validate({
        "templates": [{
            "kind": "mob",
            "source": "public_reference",
            "confidence": 0.99,
            "observation_only": True,
            "status": "production",
        }]
    })
    assert any("source must be local_capture" in error for error in errors)


def test_verified_local_template_passes():
    errors = validate({
        "templates": [{
            "kind": "player",
            "source": "local_capture",
            "confidence": 0.91,
            "observation_only": True,
            "status": "verified",
        }]
    })
    assert errors == []

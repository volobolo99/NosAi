from app.client.entity_detection import Detection, VisualEntityDetector, default_rois

def test_entity_detection_is_observation_only():
    d=Detection("player",1,2,10,10,.9)
    assert d.observation_only is True

def test_default_visual_rois_are_stable():
    rois=default_rois()
    assert {r.name for r in rois}=={"world","minimap","hud"}

def test_detector_without_templates_returns_no_guess():
    detector=VisualEntityDetector()
    assert detector.templates=={}

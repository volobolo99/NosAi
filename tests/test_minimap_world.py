from app.world_model.minimap_world import MinimapCalibration, MinimapWorldMapper


def test_minimap_mapping_preserves_origin_and_scale():
    mapper = MinimapWorldMapper(MinimapCalibration(100, 50, 2, 3))
    assert mapper.to_world(100, 50) == (0.0, 0.0)
    assert mapper.to_world(101, 51) == (2.0, 3.0)


def test_minimap_rotation_is_applied():
    mapper = MinimapWorldMapper(MinimapCalibration(0, 0, 1, 1, rotation_deg=90))
    x, y = mapper.to_world(1, 0)
    assert abs(x) < 1e-9
    assert abs(y - 1) < 1e-9

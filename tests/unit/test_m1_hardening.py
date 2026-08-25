import math
from app.m1.core.types import State, Action, Transition
from app.m1.world_model.latent import LatentWorldModel
from app.m1.world_model.ensemble import WorldModelEnsemble
from app.m1.integration import M1LearningStack


def make_data(n=48):
    out=[]
    for i in range(n):
        x=float(i%8); a=Action("move", {"delta": float((i%3)-1), "reward": float(i%5)/5.0})
        nx=x+a.parameters["delta"]+0.05*(i%2)
        out.append(Transition(State((x, x*x/8.0)), a, a.parameters["reward"], State((nx, nx*nx/8.0)), False))
    return out


def test_latent_world_model_is_learnable():
    data=make_data()
    model=LatentWorldModel(action_dim=3, latent_dim=6, seed=7)
    before=model.predict(data[0].state, data[0].action).next_state.features
    result=model.train(data, epochs=20, batch_size=16)
    after=model.predict(data[0].state, data[0].action).next_state.features
    assert result["loss"] >= 0.0
    assert model.learnable
    assert before != after
    assert math.isfinite(result["loss"])


def test_independent_ensemble_has_nonzero_disagreement_after_training():
    data=make_data()
    models=[]
    for seed in (1,2,3):
        m=LatentWorldModel(action_dim=3, latent_dim=6, seed=seed)
        m.train(data, epochs=15, batch_size=16)
        models.append(m)
    ensemble=WorldModelEnsemble(models)
    u=ensemble.uncertainty(data[0].state, data[0].action)
    assert u.epistemic >= 0.0
    assert u.confidence <= 1.0
    # Distinct bootstrap/seeded members should not collapse exactly in this small model.
    assert ensemble.disagreement(data[0].state, data[0].action) > 0.0


def test_stack_trains_real_ensemble():
    stack=M1LearningStack(reference_features=(0.0,0.0), seed=13)
    data=make_data(32)
    result=stack.train_world_model(data, epochs=8, batch_size=8)
    assert result["members"] == 3
    assert stack.world_model is not None
    assert stack.world_model.uncertainty(data[0].state, data[0].action).epistemic > 0.0

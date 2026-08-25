from app.m1.integration import M1LearningStack
from app.m1.adapters import to_m1_state, to_m1_action
from app.world_model.state import WorldState, EntityState
from app.world_model.actions import WorldAction


def make_state(hp=100):
    return WorldState(
        character={"hp": hp, "mp": 100},
        entities={"mob:1": EntityState("mob:1", "monster", {"hp": 100})},
        inventory={"potion": 2},
        map_id="sandbox",
    )


def test_m1_stack_observes_and_replays_transition():
    stack = M1LearningStack((0, 100, 100, 2, 1, 100), replay_capacity=8)
    s = make_state()
    ns = make_state()
    ns.tick = 1
    ns.entities["mob:1"].attributes["hp"] = 75
    result = stack.observe_transition(
        s, WorldAction("attack", "ATTACK", {"target_id": "mob:1", "damage": 25}), ns, 1.0, False
    )
    assert result.quality.total > 0
    assert len(stack.replay) == 1
    assert result.ood.is_ood is False


def test_m1_world_model_predicts_existing_sandbox_action():
    stack = M1LearningStack((0, 100, 100, 2, 1, 100))
    s = make_state()
    pred = stack.world_model.predict(
        to_m1_state(s),
        to_m1_action(
            WorldAction("attack", "ATTACK", {"target_id": "mob:1", "damage": 25})
        )
    )
    assert pred.reward == 1.0


def test_m1_is_optional_in_legacy_learning_loop():
    from app.learning_loop.loop import LearningLoop
    from app.rl.environment.world_env import WorldRLEnvironment
    from app.rl.q_learning import QLearningAgent
    loop = LearningLoop(WorldRLEnvironment(), QLearningAgent(seed=7), m1_stack=None)
    history = loop.train(episodes=2, max_steps=5)
    assert len(history) == 2

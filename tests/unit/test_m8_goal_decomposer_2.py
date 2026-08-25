from app.goal_planner.models import Goal
from app.m8.hierarchical import GoalDecomposer, HierarchicalPlanner


def test_goal_objective_decomposes_with_real_template_and_metadata():
    goal = Goal("g", "QUEST", "finish quest", priority=3.0,
                constraints={"target": "raid_boss", "safe": True})
    graph = GoalDecomposer().decompose(goal)
    assert [n.kind for n in graph.nodes.values()] == [
        "READ_OBJECTIVE", "LOCATE_TARGET", "TRAVEL", "COMPLETE"
    ]
    assert graph.nodes["g:sub:0"].metadata["target"] == "raid_boss"
    assert graph.nodes["g:sub:1"].prerequisites == ("g:sub:0",)
    assert graph.nodes["g:sub:3"].parent_id == "g"


def test_goal_decomposer_rejects_empty_goal():
    try:
        GoalDecomposer().decompose("g", [])
    except ValueError:
        pass
    else:
        raise AssertionError("empty decomposition must fail")


def test_goal_graph_is_cycle_safe_and_executable():
    graph = GoalDecomposer().decompose("g", ["a", "b", "c"])
    planner = HierarchicalPlanner(graph)
    completed = set()
    order = []
    while True:
        node = planner.next_subgoal(completed)
        if node is None:
            break
        order.append(node.id)
        completed.add(node.id)
    assert order == ["g.1", "g.2", "g.3"]
    assert len(completed) == 3

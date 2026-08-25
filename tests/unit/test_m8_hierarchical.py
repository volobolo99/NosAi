from app.m8.hierarchical import GoalDecomposer, HierarchicalPlanner

def test_decomposition_builds_prerequisite_chain():
    g=GoalDecomposer().decompose('g',['a','b','c']); assert g.nodes['g.2'].prerequisites==('g.1',)

def test_ready_subgoal():
    g=GoalDecomposer().decompose('g',['a','b']); assert HierarchicalPlanner(g).next_subgoal(set()).id=='g.1'

def test_replanning_excludes_invalidated():
    g=GoalDecomposer().decompose('g',['a','b']); p=HierarchicalPlanner(g); assert p.replan({'g.1'},{'g.2'})==[]

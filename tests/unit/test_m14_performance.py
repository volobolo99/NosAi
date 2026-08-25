from app.m14.performance import ParallelSimulation, MCTSOptimizer, MemoryIndex

def test_parallel_simulation(): assert ParallelSimulation().run(lambda x:x*x,[1,2,3])==[1,4,9]

def test_mcts_budget(): assert MCTSOptimizer().simulations(.5)>64

def test_memory_index():
    i=MemoryIndex(); i.add('x',1); i.add('x',2); assert i.get('x')==[1,2]

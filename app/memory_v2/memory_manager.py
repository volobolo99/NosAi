
import uuid
from .models import Observation, MemoryQuery
from .store import MemoryStore
from .working_memory import WorkingMemory
from .consolidation import MemoryConsolidator
from .retrieval import MemoryRetriever
from .strategy_learning import StrategyLearning
from app.m3.memory_graph import MemoryGraph
from app.m5_unified_memory import UnifiedMemory


class AIMemoryV2:
    def __init__(self, store=None):
        self.store = store or MemoryStore()
        self.working = WorkingMemory()
        self.consolidator = MemoryConsolidator(self.store)
        self.retriever = MemoryRetriever(self.store)
        self.strategy_learning = StrategyLearning(self.store)
        self.graph = MemoryGraph()
        self.unified = UnifiedMemory(self, self.graph)

    def ingest(self, event_type, payload, source, session_id=None, confidence=1.0):
        observation = Observation(
            id=str(uuid.uuid4()),
            event_type=event_type,
            payload=payload,
            source=source,
            session_id=session_id,
            confidence=confidence,
        )

        self.store.add_observation(observation)
        self.working.push(observation)
        self.consolidator.consolidate_observation(observation)
        for fact in self.store.facts.values():
            if observation.id in fact.source_refs:
                self.graph.from_fact(fact)

        self.unified.consolidate_graph()
        return observation

    def query(self, text, **kwargs):
        return self.retriever.retrieve(
            MemoryQuery(text=text, **kwargs)
        )

    def consolidate_knowledge(self, *, min_inference_support=2, inference_confidence=0.7, min_strategy_attempts=3, strategy_success_threshold=0.75):
        """Promote sufficiently supported inferences and strategies to stable facts."""
        promoted_inferences = self.consolidator.consolidate_inferences(
            min_support=min_inference_support,
            confidence_threshold=inference_confidence,
        )
        promoted_strategies = self.consolidator.consolidate_strategy_knowledge(
            min_attempts=min_strategy_attempts,
            success_threshold=strategy_success_threshold,
        )
        self.unified.consolidate_graph()
        return {
            "inferences": promoted_inferences,
            "strategies": promoted_strategies,
        }

    def context(self, session_id=None, recent=20):
        return {
            "recent_observations":
                self.retriever.recent_observations(recent, session_id),
            "working_memory":
                self.working.snapshot(),
        }

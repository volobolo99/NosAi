
from collections import defaultdict
from .models import (
    Observation, Episode, MemoryFact, Inference, StrategyExperience
)


class MemoryStore:
    """In-process reference store; replaceable with SQLite/PostgreSQL later."""

    def __init__(self):
        self.observations = {}
        self.episodes = {}
        self.facts = {}
        self.inferences = {}
        self.strategy_experiences = []

    def add_observation(self, item: Observation):
        self.observations[item.id] = item

    def add_episode(self, item: Episode):
        self.episodes[item.id] = item

    def add_fact(self, item: MemoryFact):
        self.facts[item.id] = item

    def add_inference(self, item: Inference):
        self.inferences[item.id] = item

    def add_strategy_experience(self, item: StrategyExperience):
        self.strategy_experiences.append(item)

    def observations_for_session(self, session_id):
        return [
            x for x in self.observations.values()
            if x.session_id == session_id
        ]

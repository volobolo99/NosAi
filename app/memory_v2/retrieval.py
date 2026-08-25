
from .models import MemoryQuery


class MemoryRetriever:
    def __init__(self, store):
        self.store = store

    def retrieve(self, query: MemoryQuery):
        candidates = []

        for fact in self.store.facts.values():
            if fact.confidence < query.min_confidence:
                continue

            haystack = " ".join([
                fact.subject,
                fact.predicate,
                str(fact.object),
            ]).lower()

            score = 0
            for token in query.text.lower().split():
                if token in haystack:
                    score += 1

            if query.entity_ids and not any(
                entity in haystack for entity in query.entity_ids
            ):
                continue

            if score:
                candidates.append((score * fact.confidence, fact))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in candidates[:query.limit]]

    def recent_observations(self, limit=20, session_id=None):
        rows = list(self.store.observations.values())
        if session_id:
            rows = [x for x in rows if x.session_id == session_id]
        rows.sort(key=lambda x: x.timestamp, reverse=True)
        return rows[:limit]

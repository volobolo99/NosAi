
from collections import defaultdict
from .models import MemoryFact, Inference


class MemoryConsolidator:
    """Turns repeated observations into facts and cautious inferences."""

    def __init__(self, store):
        self.store = store

    def consolidate_observation(self, observation):
        p = observation.payload

        # Explicit event -> directly useful fact.
        if observation.event_type == "MAP_CHANGED" and "map_id" in p:
            self._upsert_fact(
                subject=f"character:{p.get('character_id', 'current')}",
                predicate="located_at",
                object=f"map:{p['map_id']}",
                confidence=observation.confidence,
                source_ref=observation.id,
            )

        if observation.event_type == "ITEM_RECEIVED" and "item_id" in p:
            self._upsert_fact(
                subject=f"character:{p.get('character_id', 'current')}",
                predicate="received",
                object=f"item:{p['item_id']}",
                confidence=observation.confidence,
                source_ref=observation.id,
            )

    def infer_item_source(self, observations, window_seconds=10):
        """Candidate inference: defeat followed shortly by item receipt."""
        defeats = [
            x for x in observations
            if x.event_type == "MONSTER_DEFEATED"
            and "monster_id" in x.payload
        ]
        rewards = [
            x for x in observations
            if x.event_type == "ITEM_RECEIVED"
            and "item_id" in x.payload
        ]

        for defeat in defeats:
            for reward in rewards:
                delta = (reward.timestamp - defeat.timestamp).total_seconds()
                if 0 <= delta <= window_seconds:
                    self.store.add_inference(Inference(
                        id=f"{defeat.id}:{reward.id}",
                        subject=f"monster:{defeat.payload['monster_id']}",
                        predicate="probably_drops",
                        object=f"item:{reward.payload['item_id']}",
                        confidence=0.5,
                        supporting_observations=[defeat.id, reward.id],
                    ))


    def consolidate_inferences(self, min_support: int = 2, confidence_threshold: float = 0.7):
        """Promote repeatedly supported inferences into stable facts.

        Promotion is conservative: an inference must have enough supporting
        observations and confidence. The resulting fact keeps all provenance.
        """
        if min_support < 1:
            raise ValueError("min_support must be >= 1")
        promoted = []
        for inference in self.store.inferences.values():
            if inference.status == "confirmed":
                continue
            if len(inference.supporting_observations) < min_support:
                continue
            if inference.confidence < confidence_threshold:
                continue
            key = f"{inference.subject}|{inference.predicate}|{inference.object}"
            existing = self.store.facts.get(key)
            if existing is None:
                self.store.add_fact(MemoryFact(
                    id=key,
                    subject=inference.subject,
                    predicate=inference.predicate,
                    object=inference.object,
                    confidence=inference.confidence,
                    source_refs=list(inference.supporting_observations),
                ))
            else:
                existing.confidence = max(existing.confidence, inference.confidence)
                existing.source_refs = sorted(set(existing.source_refs + inference.supporting_observations))
                existing.verification_count = max(existing.verification_count, len(existing.source_refs))
            inference.status = "confirmed"
            promoted.append(key)
        return promoted

    def consolidate_strategy_knowledge(self, min_attempts: int = 3, success_threshold: float = 0.75):
        """Promote consistently successful strategies into semantic facts."""
        if min_attempts < 1:
            raise ValueError("min_attempts must be >= 1")
        grouped = defaultdict(list)
        for experience in self.store.strategy_experiences:
            grouped[(experience.goal_type, experience.strategy_id)].append(experience)
        promoted = []
        for (goal_type, strategy_id), rows in grouped.items():
            if len(rows) < min_attempts:
                continue
            success_rate = sum(1.0 for row in rows if row.success) / len(rows)
            if success_rate < success_threshold:
                continue
            key = f"strategy:{goal_type}|preferred:{strategy_id}"
            existing = self.store.facts.get(key)
            confidence = min(1.0, 0.5 + 0.5 * success_rate)
            if existing is None:
                self.store.add_fact(MemoryFact(
                    id=key,
                    subject=f"goal:{goal_type}",
                    predicate="preferred_strategy",
                    object=strategy_id,
                    confidence=confidence,
                    source_refs=[],
                ))
            else:
                existing.confidence = max(existing.confidence, confidence)
                existing.verification_count = len(rows)
            promoted.append(key)
        return promoted

    def _upsert_fact(self, subject, predicate, object, confidence, source_ref):
        key = f"{subject}|{predicate}|{object}"
        existing = self.store.facts.get(key)

        if existing:
            existing.confidence = min(
                1.0, existing.confidence * 0.7 + confidence * 0.3
            )
            existing.verification_count += 1
            existing.source_refs.append(source_ref)
            return

        self.store.add_fact(MemoryFact(
            id=key,
            subject=subject,
            predicate=predicate,
            object=object,
            confidence=confidence,
            source_refs=[source_ref],
        ))

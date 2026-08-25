from datetime import datetime, timedelta, timezone

from app.memory_v2.models import MemoryFact
from app.memory_v2.reliability import MemoryReliability


def test_reliability_decays_old_fact():
    now = datetime.now(timezone.utc)
    fact = MemoryFact("f", "a", "likes", "b", 0.8, ["s1"], last_verified=now - timedelta(days=30), verification_count=1)
    assessment = MemoryReliability(half_life_days=30).assess(fact, now=now)
    assert 0.39 < assessment.decayed_confidence < 0.41
    assert assessment.status == "stale"


def test_reliability_support_is_bounded():
    now = datetime.now(timezone.utc)
    fact = MemoryFact("f", "a", "likes", "b", 0.9, ["s1", "s2", "s3"], last_verified=now, verification_count=20)
    assessment = MemoryReliability().assess(fact, now=now)
    assert assessment.decayed_confidence <= 1.0
    assert assessment.status == "trusted"


def test_suspect_memory_is_not_usable():
    now = datetime.now(timezone.utc)
    fact = MemoryFact("f", "a", "likes", "b", 0.05, [], last_verified=now - timedelta(days=365), verification_count=1)
    reliability = MemoryReliability(half_life_days=30)
    assert reliability.assess(fact, now=now).status == "suspect"
    assert not reliability.usable(fact, now=now)

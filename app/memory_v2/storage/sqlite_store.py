
import sqlite3, json
from datetime import datetime, timezone
from pathlib import Path
from app.memory_v2.models import Observation, MemoryFact, Inference, StrategyExperience

class SQLiteMemoryStore:
    """Persistent implementation compatible with the AI Memory v2 concepts."""

    def __init__(self, path="data/ai_memory.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self._init()
        self.observations = {}
        self.facts = {}
        self.inferences = {}
        self.strategy_experiences = []
        self._load_cache()

    def _load_cache(self):
        for r in self.db.execute("SELECT * FROM observations"):
            self.observations[r["id"]] = Observation(r["id"], r["event_type"], json.loads(r["payload"]), r["source"], datetime.fromisoformat(r["timestamp"]), r["confidence"], r["session_id"])
        for r in self.db.execute("SELECT * FROM facts"):
            self.facts[r["id"]] = MemoryFact(r["id"], r["subject"], r["predicate"], json.loads(r["object_json"]), r["confidence"], json.loads(r["source_refs"]), datetime.fromisoformat(r["first_seen"]), datetime.fromisoformat(r["last_verified"]), r["verification_count"])
        for r in self.db.execute("SELECT * FROM inferences"):
            self.inferences[r["id"]] = Inference(r["id"], r["subject"], r["predicate"], json.loads(r["object_json"]), r["confidence"], json.loads(r["supporting_observations"]), r["status"])
        for r in self.db.execute("SELECT * FROM strategy_experiences ORDER BY id"):
            self.strategy_experiences.append(StrategyExperience(r["goal_type"], r["strategy_id"], bool(r["success"]), r["reward"], r["duration_seconds"], r["risk"], json.loads(r["context_json"]), datetime.fromisoformat(r["timestamp"])))

    def _init(self):
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS observations (
            id TEXT PRIMARY KEY, event_type TEXT NOT NULL,
            payload TEXT NOT NULL, source TEXT NOT NULL,
            timestamp TEXT NOT NULL, confidence REAL NOT NULL,
            session_id TEXT
        );
        CREATE TABLE IF NOT EXISTS facts (
            id TEXT PRIMARY KEY, subject TEXT NOT NULL,
            predicate TEXT NOT NULL, object_json TEXT NOT NULL,
            confidence REAL NOT NULL, source_refs TEXT NOT NULL,
            first_seen TEXT NOT NULL, last_verified TEXT NOT NULL,
            verification_count INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS inferences (
            id TEXT PRIMARY KEY, subject TEXT NOT NULL,
            predicate TEXT NOT NULL, object_json TEXT NOT NULL,
            confidence REAL NOT NULL, supporting_observations TEXT NOT NULL,
            status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS strategy_experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_type TEXT NOT NULL, strategy_id TEXT NOT NULL,
            success INTEGER NOT NULL, reward REAL NOT NULL,
            duration_seconds REAL NOT NULL, risk REAL NOT NULL,
            context_json TEXT NOT NULL, timestamp TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_obs_session ON observations(session_id);
        CREATE INDEX IF NOT EXISTS idx_obs_type ON observations(event_type);
        CREATE INDEX IF NOT EXISTS idx_exp_goal ON strategy_experiences(goal_type);
        """)
        self.db.commit()

    # MemoryStore-compatible API used by AIMemoryV2.
    def add_observation(self, x):
        self.save_observation(x)

    def add_fact(self, x):
        self.save_fact(x)

    def add_inference(self, x):
        self.save_inference(x)

    def add_strategy_experience(self, x):
        self.save_strategy_experience(x)

    def save_observation(self, x):
        self.observations[x.id] = x
        self.db.execute("""INSERT OR REPLACE INTO observations
        VALUES (?,?,?,?,?,?,?)""", (
            x.id, x.event_type, json.dumps(x.payload),
            x.source, x.timestamp.isoformat(), x.confidence, x.session_id))
        self.db.commit()

    def save_fact(self, x):
        self.facts[x.id] = x
        self.db.execute("""INSERT OR REPLACE INTO facts
        VALUES (?,?,?,?,?,?,?,?,?)""", (
            x.id, x.subject, x.predicate, json.dumps(x.object),
            x.confidence, json.dumps(x.source_refs),
            x.first_seen.isoformat(), x.last_verified.isoformat(),
            x.verification_count))
        self.db.commit()

    def save_inference(self, x):
        self.inferences[x.id] = x
        self.db.execute("""INSERT OR REPLACE INTO inferences
        VALUES (?,?,?,?,?,?,?)""", (
            x.id, x.subject, x.predicate, json.dumps(x.object),
            x.confidence, json.dumps(x.supporting_observations), x.status))
        self.db.commit()

    def save_strategy_experience(self, x):
        self.strategy_experiences.append(x)
        self.db.execute("""INSERT INTO strategy_experiences
        (goal_type,strategy_id,success,reward,duration_seconds,risk,context_json,timestamp)
        VALUES (?,?,?,?,?,?,?,?)""", (
            x.goal_type, x.strategy_id, int(x.success), x.reward,
            x.duration_seconds, x.risk, json.dumps(x.context),
            x.timestamp.isoformat()))
        self.db.commit()

    def count(self, table):
        allowed={"observations","facts","inferences","strategy_experiences"}
        if table not in allowed: raise ValueError("invalid table")
        return self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def close(self):
        self.db.close()

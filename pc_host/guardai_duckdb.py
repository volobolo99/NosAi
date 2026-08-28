from pathlib import Path
import duckdb

class GuardAiDuckDB:
    def __init__(self, database_path="data/guardai/replay.duckdb", schema_path="config/schema.sql"):
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(database_path)
        self.conn.execute(Path(schema_path).read_text(encoding="utf-8"))

    def insert_perception_frame(self, frame):
        self.conn.execute(
            "INSERT OR REPLACE INTO telemetry_frames VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [frame.frame_id, frame.presentation_timestamp_us, frame.threat_level,
             frame.disagreement_delta,
             frame.player_position.x if frame.HasField("player_position") else None,
             frame.player_position.y if frame.HasField("player_position") else None,
             frame.player_position.z if frame.HasField("player_position") else None,
             frame.system_status_flags],
        )

    def close(self):
        self.conn.close()

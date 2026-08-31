CREATE TABLE IF NOT EXISTS telemetry_frames (
    frame_id BIGINT PRIMARY KEY, timestamp_us BIGINT NOT NULL,
    threat_level FLOAT NOT NULL, disagreement_delta FLOAT NOT NULL,
    player_x FLOAT, player_y FLOAT, player_z FLOAT, system_status INTEGER
);
CREATE TABLE IF NOT EXISTS failure_analytics (
    event_id SEQUENCE, frame_id BIGINT, pos_x FLOAT NOT NULL, pos_y FLOAT NOT NULL, pos_z FLOAT NOT NULL,
    resource_level FLOAT NOT NULL, threat_level FLOAT NOT NULL, stamina_level FLOAT NOT NULL,
    action_taken INTEGER NOT NULL, failure_category VARCHAR(64),
    FOREIGN KEY (frame_id) REFERENCES telemetry_frames(frame_id)
);
CREATE TABLE IF NOT EXISTS mcts_decision_logs (
    frame_id BIGINT, policy_id VARCHAR(128), utility_score FLOAT,
    simulations_count INTEGER, execution_time_ms FLOAT, PRIMARY KEY (frame_id, policy_id)
);
CREATE INDEX IF NOT EXISTS idx_failure_coords ON failure_analytics (threat_level, stamina_level);
CREATE INDEX IF NOT EXISTS idx_telemetry_time ON telemetry_frames (timestamp_us);

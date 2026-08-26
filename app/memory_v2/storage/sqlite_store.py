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
        queries = {
            "observations": "SELECT COUNT(*) FROM observations",
            "facts": "SELECT COUNT(*) FROM facts",
            "inferences": "SELECT COUNT(*) FROM inferences",
            "strategy_experiences": "SELECT COUNT(*) FROM strategy_experiences",
        }
        query = queries.get(table)
        if query is None:
            raise ValueError("invalid table")
        return self.db.execute(query).fetchone()[0]

    def close(self):
        self.db.close()
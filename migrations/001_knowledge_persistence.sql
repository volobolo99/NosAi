CREATE TABLE knowledge_records (
    id UUID PRIMARY KEY,
    repository TEXT NOT NULL,
    project TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('episodic','semantic','procedural','repository','evaluation')),
    status TEXT NOT NULL CHECK (status IN ('candidate','verified','durable','rejected','superseded')),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_run UUID,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX knowledge_records_scope_idx ON knowledge_records (repository, project, kind, status);
CREATE INDEX knowledge_records_source_run_idx ON knowledge_records (source_run);

CREATE TABLE knowledge_evidence (
    id UUID PRIMARY KEY,
    knowledge_id UUID NOT NULL REFERENCES knowledge_records(id) ON DELETE RESTRICT,
    run_id UUID,
    outcome TEXT NOT NULL CHECK (outcome IN ('supports','contradicts','neutral')),
    summary TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX knowledge_evidence_knowledge_idx ON knowledge_evidence (knowledge_id, created_at DESC);
CREATE INDEX knowledge_evidence_run_idx ON knowledge_evidence (run_id);

CREATE TABLE knowledge_links (
    source_id UUID NOT NULL REFERENCES knowledge_records(id) ON DELETE RESTRICT,
    target_id UUID NOT NULL REFERENCES knowledge_records(id) ON DELETE RESTRICT,
    relation TEXT NOT NULL CHECK (relation IN ('supports','contradicts','refines','supersedes','related')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (source_id, target_id, relation),
    CHECK (source_id <> target_id)
);

CREATE INDEX knowledge_links_target_idx ON knowledge_links (target_id, relation);

CREATE TABLE knowledge_embeddings (
    knowledge_id UUID PRIMARY KEY REFERENCES knowledge_records(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL CHECK (dimensions > 0),
    embedding_json JSONB,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE knowledge_audit (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id UUID NOT NULL REFERENCES knowledge_records(id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    previous_status TEXT,
    new_status TEXT,
    reason TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX knowledge_audit_knowledge_idx ON knowledge_audit (knowledge_id, created_at DESC);

CREATE OR REPLACE FUNCTION prevent_knowledge_evidence_update_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'knowledge_evidence is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER knowledge_evidence_immutable
BEFORE UPDATE OR DELETE ON knowledge_evidence
FOR EACH ROW EXECUTE FUNCTION prevent_knowledge_evidence_update_delete();

CREATE OR REPLACE FUNCTION prevent_knowledge_audit_update_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'knowledge_audit is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER knowledge_audit_immutable
BEFORE UPDATE OR DELETE ON knowledge_audit
FOR EACH ROW EXECUTE FUNCTION prevent_knowledge_audit_update_delete();

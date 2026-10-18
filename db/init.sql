CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    source_url TEXT NOT NULL,
    election_year INTEGER NOT NULL,
    dignity TEXT NOT NULL,
    canton TEXT,
    candidate_name TEXT NOT NULL,
    organization TEXT,
    sha256 TEXT NOT NULL UNIQUE,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_start INTEGER NOT NULL,
    page_end INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS chunks_document_idx ON chunks(document_id);
CREATE INDEX IF NOT EXISTS chunks_content_fts_idx ON chunks USING GIN (to_tsvector('spanish', content));

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,
    channel TEXT NOT NULL CHECK (channel IN ('web', 'whatsapp')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

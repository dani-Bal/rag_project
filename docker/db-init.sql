CREATE DATABASE rag_project;


-- ============================================
-- RAG PROJECT – DATENBANKSCHEMA
-- PostgreSQL + pgvector
-- ============================================

-- 1. Erweiterungen
CREATE EXTENSION IF NOT EXISTS vector;


-- 2. PDF-Metadaten
CREATE TABLE IF NOT EXISTS pdf_metadata (
    id BIGSERIAL PRIMARY KEY,
    title TEXT,
    author TEXT,
    subject TEXT,
    keywords TEXT,
    pdf_created_at TIMESTAMPTZ,
    page_count INTEGER,
    file_size_bytes BIGINT
);


-- 3. Dokumente
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    content TEXT,
    original_file BYTEA,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    metadata_id BIGINT UNIQUE
        REFERENCES pdf_metadata(id)
        ON DELETE SET NULL
);


-- 4. Chunking-Durchläufe
CREATE TABLE IF NOT EXISTS chunking_runs (
    id BIGSERIAL PRIMARY KEY,

    document_id BIGINT NOT NULL
        REFERENCES documents(id)
        ON DELETE CASCADE,

    strategy VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding_model TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- 5. Chunks mit Embeddings
CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,

    run_id BIGINT NOT NULL
        REFERENCES chunking_runs(id)
        ON DELETE CASCADE,

    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER,
    embedding VECTOR(384),

    UNIQUE (run_id, chunk_index)
);


-- 6. Indizes
CREATE INDEX IF NOT EXISTS idx_chunking_runs_document_id
    ON chunking_runs(document_id);

CREATE INDEX IF NOT EXISTS idx_chunks_run_id
    ON chunks(run_id);

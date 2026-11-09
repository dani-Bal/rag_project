-- ============================================
-- RAG PROJECT - DATABASE SCHEMA
-- PostgreSQL 18 + pgvector
-- ============================================

BEGIN;

-- pgvector aktivieren
CREATE EXTENSION IF NOT EXISTS vector;


-- ============================================
-- 1. PDF METADATA
-- ============================================

CREATE TABLE IF NOT EXISTS pdf_metadata (
    id BIGSERIAL PRIMARY KEY,

    title TEXT NULL,
    author TEXT NULL,
    subject TEXT NULL,
    keywords TEXT NULL,

    pdf_created_at TIMESTAMPTZ NULL,
    page_count INTEGER NULL,
    file_size_bytes BIGINT NULL
);


-- ============================================
-- 2. DOCUMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,

    filename TEXT NOT NULL,
    content TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    metadata_id BIGINT NULL UNIQUE,

    CONSTRAINT fk_documents_metadata
        FOREIGN KEY (metadata_id)
        REFERENCES pdf_metadata(id)
        ON DELETE SET NULL
);


-- ============================================
-- 3. CHUNKING RUNS
-- ============================================

CREATE TABLE IF NOT EXISTS chunking_runs (
    id BIGSERIAL PRIMARY KEY,

    document_id BIGINT NOT NULL,

    strategy VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}',
    embedding_model TEXT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_chunking_runs_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE
);


-- ============================================
-- 4. CHUNKS
-- ============================================

CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,

    run_id BIGINT NOT NULL,
    chunk_index INTEGER NOT NULL,

    content TEXT NOT NULL,
    token_count INTEGER NULL,
    embedding VECTOR(384) NULL,

    CONSTRAINT fk_chunks_run
        FOREIGN KEY (run_id)
        REFERENCES chunking_runs(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_chunks_run_index
        UNIQUE (run_id, chunk_index)
);


-- ============================================
-- 5. INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_chunks_run_id
    ON chunks(run_id);

CREATE INDEX IF NOT EXISTS idx_chunking_runs_document_id
    ON chunking_runs(document_id);


COMMIT;
"""Minimal Ollama chat agent for local smoke testing.

The retrieval tool, PostgreSQL session storage, and Qdrant integration are
intentionally disabled until the basic agent connection has been verified.
"""

import asyncio
import logging
import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

chat_model = os.getenv("CHAT_MODEL", "openai:gpt-4o-mini").removeprefix("openai:")

agent = Agent(
    OpenAIChatModel(chat_model),
    instructions=(
        "You are a helpful local assistant. Answer clearly and concisely. "
        "No retrieval tools are enabled in this smoke-test mode."
    ),
)


# Retrieval is intentionally disabled for now. Re-enable this tool after the
# basic Ollama chat path has been verified and PostgreSQL/Qdrant are available.
# @agent.tool
# async def search_documents(query: str, limit: int = 5) -> list[dict]:
#     """Find relevant document passages in the knowledge base."""
#     ...

# The previous RAG implementation is preserved here for later re-enablement.
# It is commented out intentionally, so this smoke-test agent does not import
# or connect to PostgreSQL/Qdrant and does not expose any tools.
#
# import json
# import time
# from dataclasses import dataclass, field
#
# import asyncpg
# from openai import AsyncOpenAI
# from pydantic_ai import ModelMessagesTypeAdapter, RunContext, UsageLimits
# from pydantic_ai.exceptions import UsageLimitExceeded
# from qdrant_client import AsyncQdrantClient, models
#
# @dataclass
# class SessionState:
#     summary: str = ""
#     active_document_ids: list[str] = field(default_factory=list)
#
# @dataclass
# class Deps:
#     tenant_id: str
#     state: SessionState
#     qdrant: AsyncQdrantClient
#     openai: AsyncOpenAI
#
# @agent.instructions
# def session_instructions(ctx: RunContext[Deps]) -> str:
#     return (
#         f"Session summary: {ctx.deps.state.summary or '(none)'}\n"
#         f"Previously relevant documents: {ctx.deps.state.active_document_ids}"
#     )
#
# @agent.tool
# async def search_documents(
#     ctx: RunContext[Deps], query: str, limit: int = 5
# ) -> list[dict]:
#     """Find relevant document passages in the tenant's knowledge base."""
#     start = time.perf_counter()
#     try:
#         embedding = await ctx.deps.openai.embeddings.create(
#             model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"), input=query
#         )
#         response = await ctx.deps.qdrant.query_points(
#             collection_name=os.getenv("QDRANT_COLLECTION", "documents"),
#             query=embedding.data[0].embedding,
#             query_filter=models.Filter(
#                 must=[
#                     models.FieldCondition(
#                         key="tenant_id", match=models.MatchValue(value=ctx.deps.tenant_id)
#                     )
#                 ]
#             ),
#             limit=max(1, min(limit, 10)),
#             with_payload=True,
#         )
#         hits = []
#         for point in response.points:
#             payload = point.payload or {}
#             doc_id = payload.get("document_id")
#             hits.append(
#                 {"document_id": doc_id, "text": payload.get("text", ""), "score": point.score}
#             )
#             if doc_id and doc_id not in ctx.deps.state.active_document_ids:
#                 ctx.deps.state.active_document_ids.append(doc_id)
#         logging.getLogger("pydantic_rag").info(
#             "tool=search_documents ok hits=%d duration_ms=%.0f",
#             len(hits),
#             (time.perf_counter() - start) * 1000,
#         )
#         return hits
#     except Exception:
#         logging.getLogger("pydantic_rag").exception("tool=search_documents failed")
#         raise
#
# async def setup(pool: asyncpg.Pool) -> None:
#     await pool.execute("""
#         CREATE TABLE IF NOT EXISTS pydantic_agent_sessions (
#             tenant_id TEXT NOT NULL,
#             session_id TEXT NOT NULL,
#             messages JSONB NOT NULL DEFAULT '[]'::jsonb,
#             state JSONB NOT NULL DEFAULT '{}'::jsonb,
#             PRIMARY KEY (tenant_id, session_id)
#         )
#     """)


async def main() -> None:
    print("Pydantic AI + Ollama smoke test. Type 'exit' to quit.")
    while True:
        question = await asyncio.to_thread(input, "You: ")
        if question.strip().lower() == "exit":
            break
        result = await agent.run(question)
        print("Agent:", result.output)


if __name__ == "__main__":
    asyncio.run(main())

"""Define all tools for usage in the agent."""

from pydantic_ai import RunContext
from sqlalchemy import select

from rag_project.agent.models import AgentContext, DocumentChunk
from rag_project.database.models import DocumentChunk as DocumentChunkDB


def retrieve_most_relevant_documents(
    ctx: RunContext[AgentContext],
    query: str,
    num_docs: int,
) -> list[DocumentChunk]:
    """Retrieve the semantically most relevant documents for a query.

    Args:
        ctx (RunContext[AgentContext]): The agent context, used for dependency injection.
        query (str): The user query to find relevant documents for.
        num_docs (int): The number of documents to return at most

    Returns:
        list[DocumentChunk]: The most relevant documents for this query.
    """
    embedding_client = ctx.deps.embedding_client

    session = ctx.deps.session

    embedding_response = embedding_client.embeddings.create(
        model=ctx.deps.embedding_model_name,
        input=query,
    )
    embedded_query = embedding_response.data[0].embedding

    db_chunks = session.scalars(
        select(DocumentChunkDB)
        .order_by(DocumentChunkDB.embedding.l2_distance(embedded_query))
        .limit(num_docs)
    )
    return [DocumentChunk(text=db_chunk.text, title=db_chunk.title) for db_chunk in db_chunks]

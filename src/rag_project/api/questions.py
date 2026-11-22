import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from sqlalchemy.orm import Session

from rag_project.agent.models import AgentContext
from rag_project.api.dependencies import get_agent, get_embedding_client, get_session
from rag_project.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questions", tags=["Questions"])


class QuestionRequest(BaseModel):
    # ... bedeutet Pflichtfeld, min_length=1 bedeutet, dass die Frage mindestens 1 Zeichen lang sein muss
    question: str = Field(..., min_length=1)


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post(
    "",
    responses={
        500: {
            "description": "Verarbeitung der Frage fehlgeschlagen. Bitte versuchen Sie es erneut."
        }
    },
)
def ask_question(
    request: QuestionRequest,
    session: Annotated[Session, Depends(get_session)],
    agent: Annotated[Agent, Depends(get_agent)],
    embedding_client: Annotated[OpenAI, Depends(get_embedding_client)],
) -> QuestionResponse:
    settings = get_settings()

    try:
        context = AgentContext(
            session=session,
            embedding_client=embedding_client,
            embedding_model_name=settings.embedding_model,
        )
        result = agent.run_sync(request.question, deps=context)

    except Exception as exc:
        logger.exception("Fehler beim beantworten der Frage")
        raise HTTPException(
            status_code=500,
            detail="Ein unerwarteter Fehler ist aufgetreten. Versuchen Sie es bitte später erneut.",
        ) from exc
    return QuestionResponse(answer=result.output, sources=[])

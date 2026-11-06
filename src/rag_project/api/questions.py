from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/questions", tags=["Questions"])


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("")
def ask_question(request: QuestionRequest) -> QuestionResponse:
    return QuestionResponse(answer="This is a placeholder answer.", sources=[])

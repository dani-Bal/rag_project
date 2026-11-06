from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/questions", tags=["Questions"])


class QuestionRequest(BaseModel):
    # ... bedeutet Pflichtfeld, min_length=1 bedeutet, dass die Frage mindestens 1 Zeichen lang sein muss
    question: str = Field(..., min_length=1)


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]


@router.post("")
def ask_question(request: QuestionRequest) -> QuestionResponse:
    return QuestionResponse(answer="This is a placeholder answer.", sources=[])

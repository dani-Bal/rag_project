from dataclasses import dataclass

from openai import OpenAI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session


class DocumentChunk(BaseModel):
    title: str = Field(description="Title of the doc")
    text: str = Field(description="Text contained in the chunk")
    vector: list[float] = Field(description="The vector representation of the chunk")


@dataclass
class AgentContext:
    session: Session
    embedding_client: OpenAI
    embedding_model_name: str

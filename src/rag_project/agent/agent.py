from collections.abc import Callable
from typing import Any, Final

from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

from rag_project.agent.models import AgentContext
from rag_project.config import get_settings

SYSTEM_PROMPT: Final[str] = (
    "You are an assistant to help find users info in their document knowledge base."
)


def build_agent(tools: list[Callable[..., Any]]) -> Agent:
    settings = get_settings()
    model = OllamaModel(
        model_name=settings.llm_model_name,
        provider=OllamaProvider(base_url=settings.llm_provider_url),
    )
    return Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=tools, deps_type=AgentContext)

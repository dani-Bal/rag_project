from collections.abc import Callable
from typing import Any, Final

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from rag_project.agent.models import AgentContext
from rag_project.config import get_settings

SYSTEM_PROMPT: Final[str] = (
    "You are an assistant to help find users info in their document knowledge base."
)


def build_agent(tools: list[Callable[..., Any]]) -> Agent:
    settings = get_settings()
    model = OpenAIChatModel(
        provider=OpenAIProvider(base_url=settings.llm_provider_url, api_key=settings.llm_api_key),
        model_name=settings.llm_model_name,
    )
    return Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=tools, deps_type=AgentContext)

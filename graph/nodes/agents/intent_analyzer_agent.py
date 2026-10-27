from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from pydantic import Field, BaseModel

from backend.service.agent_service import agent_service
from backend.service.model_service import model_service
from graph.common import IntentType, SupportedAgent
from graph.prompts import analyzer_prompt


_intent_analyzer = agent_service.get_by_name(SupportedAgent.INTENT_ANALYZER)
_intent_analyzer_model = model_service.get_by_id(_intent_analyzer.model_id)


@dataclass
class IntentAnalyzerResponse(BaseModel):
    intent_types: list[IntentType] = Field(default_factory=list, description="Minimal required intent types for the query.")

intent_analyzer_agent = create_agent(
    model=init_chat_model(
        **_intent_analyzer_model.to_dict(),
        temperature=0,
    ),
    system_prompt=analyzer_prompt(),
    response_format=IntentAnalyzerResponse,
)

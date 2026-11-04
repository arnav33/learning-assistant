from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from backend.service.agent_service import agent_service
from backend.service.model_service import model_service
from graph.common import SupportedAgent
from graph.prompts import scorer_prompt


_scorer = agent_service.get_by_name(SupportedAgent.SCORER)
_scorer_model = model_service.get_by_id(_scorer.model_id)


class ScorerAgentResponse(BaseModel):
    score: float = Field(description="The score of the webpage chunk based on the query", ge=0, le=1)


_model = init_chat_model(
    **_scorer_model.to_dict(),
    temperature=0,
    num_ctx=1000,
    num_predict=64,
).with_structured_output(ScorerAgentResponse, method="json_schema")


def _invoke(payload: dict) -> ScorerAgentResponse:
    return _model.invoke([
        SystemMessage(content=scorer_prompt()),
        *payload["messages"],
    ])


scorer_agent = RunnableLambda(_invoke)

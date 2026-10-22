from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from backend.service.agent_service import agent_service
from backend.service.model_service import model_service
from config import SupportedAgent
from graph.agent_response import AgentResponse
from prompts.formatter_prompt import formatter_prompt

_format_agent = agent_service.get_by_name(SupportedAgent.FORMATTER)
_format_model = model_service.get_by_id(_format_agent.model_id)

formatter_agent = create_agent(
    model=init_chat_model(**_format_model.to_dict()),
    system_prompt=formatter_prompt(_format_agent.performance_reviews),
)

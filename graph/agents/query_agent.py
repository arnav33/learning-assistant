from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from backend.service.agent_service import agent_service
from backend.service.model_service import model_service
from config import SupportedAgent
from prompts.query_system_prompt import query_system_prompt

_query_agent = agent_service.get_by_name(SupportedAgent.QUERY)
_query_model = model_service.get_by_id(_query_agent.model_id)

query_agent = create_agent(
    model=init_chat_model(**_query_model.to_dict()),
    system_prompt=query_system_prompt(_query_agent.performance_reviews),
)

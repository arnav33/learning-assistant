from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from backend.service.agent_service import agent_service
from backend.service.model_service import model_service
from graph.common import SupportedAgent

_proofreader = agent_service.get_by_name(SupportedAgent.PROOFREADER)
_proofreader_model = model_service.get_by_id(_proofreader.model_id)

proofreader_agent = create_agent(
    model=init_chat_model(**_proofreader_model.to_dict(), temperature=0),
)

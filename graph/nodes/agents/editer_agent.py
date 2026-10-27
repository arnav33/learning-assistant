from langchain.agents import AgentState, create_agent
from langchain.chat_models import init_chat_model

from backend.service.agent_service import agent_service
from backend.service.model_service import model_service
from config import SupportedAgent


_editer = agent_service.get_by_name(SupportedAgent.EDITER)
_editer_model = model_service.get_by_id(_editer.model_id)

editer_agent = create_agent(
    model=init_chat_model(
        **_editer_model.to_dict(),
        temperature=0.2,
        num_predict=250,
    ),
)

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from backend.service.agent_service import agent_service
from backend.service.model_service import model_service
from graph.common import SupportedAgent

_coder = agent_service.get_by_name(SupportedAgent.CODER)
_coder_model = model_service.get_by_id(_coder.model_id)

coder_agent = create_agent(
    model=init_chat_model(
        **_coder_model.to_dict(),
        temperature=0,
        num_predict=1000,
    )
)

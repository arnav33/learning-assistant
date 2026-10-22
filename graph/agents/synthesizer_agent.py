from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from backend.service.agent_service import agent_service
from backend.service.model_service import model_service
from config import SupportedAgent
from prompts.synthesizer_prompt import synthesizer_prompt
_synthesis_agent = agent_service.get_by_name(SupportedAgent.SYNTHESIS)
_synthesis_model = model_service.get_by_id(_synthesis_agent.model_id)

synthesizer_agent = create_agent(
    model=init_chat_model(**_synthesis_model.to_dict()),
    system_prompt=synthesizer_prompt(_synthesis_agent.performance_reviews),
)

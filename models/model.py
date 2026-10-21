from backend.service.model_service import model_service
from backend.service.agent_service import agent_service
from config import SupportedAgent

_search_model_id = agent_service.get_by_name(SupportedAgent.SEARCH).model_id
search_model = model_service.get_by_id(_search_model_id).to_dict()




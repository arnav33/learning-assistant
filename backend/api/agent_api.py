from backend.api.base_api import BaseAPI
from backend.service.agent_service import agent_service
from persistence.entity.agent_entity import AgentEntity


class AgentAPI(BaseAPI[AgentEntity]):
    pass


router = AgentAPI(agent_service).router

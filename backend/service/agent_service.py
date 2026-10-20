from backend.service.base_service import BaseService
from persistence.entity.agent_entity import AgentEntity
from persistence.repositories import repositories


class AgentService(BaseService[AgentEntity]):
    """Business operations for agent records."""


agent_service = AgentService(repositories.agent)

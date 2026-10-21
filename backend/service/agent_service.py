from typing import Optional

from backend.service.base_service import BaseService
from persistence.agent_repository import AgentRepository
from persistence.entity.agent_entity import AgentEntity
from persistence.repositories import repositories


class AgentService(BaseService[AgentEntity]):
    """Business operations for agent records."""

    def __init__(self, repository: AgentRepository):
        super().__init__(repository)
        self._agents = repository

    def get_by_name(self, name: str) -> Optional[AgentEntity]:
        return self._agents.get_by_name(name)


agent_service = AgentService(repositories.agent)

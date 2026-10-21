from abc import abstractmethod
from typing import Optional

from persistence.base_repository import BaseRepository
from persistence.entity.agent_entity import AgentEntity


class AgentRepository(BaseRepository[AgentEntity]):
    """Abstract contract for agent records."""

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[AgentEntity]:
        """Returns one agent by its name, or None when it is missing."""

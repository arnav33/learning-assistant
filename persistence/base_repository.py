from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from persistence.entity.base_entity import BaseEntity

EntityT = TypeVar("EntityT", bound=BaseEntity)


class BaseRepository(ABC, Generic[EntityT]):
    """CRUD contract shared by every entity repository."""

    @abstractmethod
    def create(self, entity: EntityT) -> str:
        """Inserts a record and returns its id."""

    @abstractmethod
    def get_all(self) -> List[EntityT]:
        """Returns every record."""

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[EntityT]:
        """Returns one record by id, or None when it is missing."""

    @abstractmethod
    def update(self, entity_id: str, entity: EntityT) -> bool:
        """Updates a record. Returns True when a row changed."""

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Deletes a record. Returns True when a row was removed."""

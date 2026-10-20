from typing import Generic, List, Optional, TypeVar

from persistence.base_repository import BaseRepository
from persistence.entity.base_entity import BaseEntity

EntityT = TypeVar("EntityT", bound=BaseEntity)


class BaseService(Generic[EntityT]):
    """CRUD operations shared by every entity service."""

    def __init__(self, repository: BaseRepository[EntityT]):
        self._repository = repository

    def get_all(self) -> List[EntityT]:
        return self._repository.get_all()

    def get_by_id(self, entity_id: str) -> Optional[EntityT]:
        return self._repository.get_by_id(entity_id)

    def create(self, entity: EntityT) -> str:
        return self._repository.create(entity)

    def update(self, entity_id: str, entity: EntityT) -> bool:
        return self._repository.update(entity_id, entity)

    def delete(self, entity_id: str) -> bool:
        return self._repository.delete(entity_id)

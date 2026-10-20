from typing import List, Optional

from persistence.entity.model_entity import ModelEntity
from persistence.model_repository import ModelRepository
from persistence.repositories import repositories


class ModelService:
    """Business operations for model records."""

    def __init__(self, repository: ModelRepository):
        self._repository = repository

    def get_all(self) -> List[ModelEntity]:
        return self._repository.get_all()

    def get_by_id(self, model_id: str) -> Optional[ModelEntity]:
        return self._repository.get_by_id(model_id)

    def create(self, model: ModelEntity) -> str:
        return self._repository.create(model)

    def update(self, model_id: str, model: ModelEntity) -> bool:
        return self._repository.update(model_id, model)

    def delete(self, model_id: str) -> bool:
        return self._repository.delete(model_id)


model_service = ModelService(repositories.models)

from typing import Optional

from backend.service.base_service import BaseService
from persistence.entity.model_entity import ModelEntity
from persistence.model_repository import ModelRepository
from persistence.repositories import repositories


class ModelService(BaseService[ModelEntity]):
    """Business operations for model records."""

    def __init__(self, repository: ModelRepository):
        super().__init__(repository)
        self._models = repository

    def get_by_name(self, name: str) -> Optional[ModelEntity]:
        return self._models.get_by_name(name)


model_service = ModelService(repositories.entity)

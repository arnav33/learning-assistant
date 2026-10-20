from backend.service.base_service import BaseService
from persistence.entity.model_entity import ModelEntity
from persistence.repositories import repositories


class ModelService(BaseService[ModelEntity]):
    """Business operations for model records."""


model_service = ModelService(repositories.entity)

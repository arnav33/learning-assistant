from persistence.base_repository import BaseRepository
from persistence.entity.model_entity import ModelEntity


class ModelRepository(BaseRepository[ModelEntity]):
    """Abstract contract for model records."""

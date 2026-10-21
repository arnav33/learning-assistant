from abc import abstractmethod
from typing import Optional

from persistence.base_repository import BaseRepository
from persistence.entity.model_entity import ModelEntity


class ModelRepository(BaseRepository[ModelEntity]):
    """Abstract contract for model records."""

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[ModelEntity]:
        """Returns one model by its name, or None when it is missing."""

# File: /persistence/model_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from persistence.entity.model_entity import ModelEntity

class ModelRepository(ABC):
    """Abstract contract enforcing CRUD operations using ModelEntity types."""

    @abstractmethod
    def create(self, entity: ModelEntity) -> str:
        """Inserts a new model entity. Returns the generated string ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[ModelEntity]:
        """Retrieves all model entities from the database."""
        pass

    @abstractmethod
    def get_by_id(self, model_id: str) -> Optional[ModelEntity]:
        """Retrieves a single model entity by its unique string ID."""
        pass

    @abstractmethod
    def update(self, model_id: str, entity: ModelEntity) -> bool:
        """Updates an existing model entity record. Returns True if successful."""
        pass

    @abstractmethod
    def delete(self, model_id: str) -> bool:
        """Removes a model entity record by its ID. Returns True if successful."""
        pass

from dataclasses import dataclass

from persistence.entity.base_entity import BaseEntity


@dataclass
class ModelEntity(BaseEntity):
    """Defines the core data structure and mapping rules for the model entity."""

    model: str
    model_provider: str
    thinking_budget: int
    active: bool

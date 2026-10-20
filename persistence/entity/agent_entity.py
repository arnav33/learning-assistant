from dataclasses import dataclass

from persistence.entity.base_entity import BaseEntity


@dataclass
class AgentEntity(BaseEntity):
    """Defines the core data structure and mapping rules for the model entity."""

    name: str
    description: str
    model_id: str
    active: bool
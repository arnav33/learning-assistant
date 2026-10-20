# File: /src/service/persistence/entities/model_entity.py
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

@dataclass
class ModelEntity:
    """Defines the core data structure and mapping rules for the model entity."""
    
    id: str
    model: str
    model_provider: str
    thinking_budget: int
    active: bool
    created_by: Optional[str]
    created_time: str
    last_modified_by: Optional[str]
    last_modified_time: str

    @classmethod
    def from_db_row(cls, row: tuple) -> "ModelEntity":
        """Maps a raw database row tuple into a structured ModelEntity instance."""
        return cls(
            id=row[0],
            model=row[1],
            model_provider=row[2],
            thinking_budget=int(row[3]),
            active=bool(row[4]),  # Safely maps the SQLite integer (0/1) to a boolean
            created_by=row[5],
            created_time=row[6],
            last_modified_by=row[7],
            last_modified_time=row[8]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the entity fields into a native dictionary for the API layer."""
        return asdict(self)

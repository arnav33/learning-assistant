from dataclasses import asdict, dataclass, fields
from typing import Any, Dict, Optional, get_args, get_origin, get_type_hints


@dataclass
class BaseEntity:
    id: str
    created_by: Optional[str]
    created_time: Optional[str]
    last_modified_by: Optional[str]
    last_modified_time: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_db_row(cls, row):
        hints = get_type_hints(cls)
        values = {
            field.name: _coerce(row[field.name], hints[field.name])
            for field in fields(cls)
        }
        return cls(**values)


def _coerce(value: Any, hint: Any) -> Any:
    if value is None:
        return None

    origin = get_origin(hint)
    if origin is not None:
        args = [arg for arg in get_args(hint) if arg is not type(None)]
        if len(args) == 1:
            hint = args[0]

    if hint is bool:
        return bool(value)
    if hint is int:
        return int(value)
    return value

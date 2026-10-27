from enum import Enum


class SupportedDatabase(str, Enum):
    """Supported database engine types for the application persistence layer."""
    IN_MEMORY = "in_memory"
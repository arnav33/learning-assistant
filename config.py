# File: /config.py
from typing import Literal

from enum import Enum

class SupportedDatabase(str, Enum):
    """Supported database engine types for the application persistence layer."""
    IN_MEMORY = "in_memory"

class SupportedAgent(str, Enum):
    """Supported database engine types for the application persistence layer."""
    SEARCH = "search"

DATABASE_TYPE: SupportedDatabase = SupportedDatabase.IN_MEMORY

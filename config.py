# File: /config.py
from typing import Literal

from enum import Enum

class SupportedDatabase(str, Enum):
    """Supported database engine types for the application persistence layer."""
    IN_MEMORY = "in_memory"

class SupportedAgent(str, Enum):
    """Supported database engine types for the application persistence layer."""
    QUERY = "query"
    SYNTHESIZER = "synthesizer"
    FORMATTER = "formatter"

class ToolConfig(str, Enum):
    PAGE_SIZE = 20
    OLDEST_RESULT_LIMIT = 5

DATABASE_TYPE: SupportedDatabase = SupportedDatabase.IN_MEMORY

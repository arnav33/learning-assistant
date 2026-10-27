# File: /config.py
from typing import Literal

from enum import Enum

class SupportedDatabase(str, Enum):
    """Supported database engine types for the application persistence layer."""
    IN_MEMORY = "in_memory"

class SupportedAgent(str, Enum):
    """Supported database engine types for the application persistence layer."""
    PROOFREADER = "proofreader"
    EDITER = "editer"
    SUMMARIZER = "summarizer"

class ToolConfig(str, Enum):
    PAGE_SIZE = 20
    OLDEST_RESULT_LIMIT = 5

class LocalModel:
    def __init__(self, model: str, model_provider: str) -> None:
        self.model = model
        self.model_provider = model_provider

llama3p2_1b = LocalModel(
    model="llama3.2:1b",
    model_provider="ollama",
)

qwen2p5_1p5b = LocalModel(
    model="qwen2.5:1.5b",
    model_provider="ollama",
)

qwen_0p5b = LocalModel(
    model="qwen:0.5b",
    model_provider="ollama",
)

default_local_model = qwen2p5_1p5b


DATABASE_TYPE: SupportedDatabase = SupportedDatabase.IN_MEMORY
MODEL_NUM_CTX = 65536




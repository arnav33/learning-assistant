# File: /config.py
from typing import Literal

from enum import Enum

from graph.common import LocalModel, SupportedDatabase

class ToolConfig(str, Enum):
    PAGE_SIZE = 20
    OLDEST_RESULT_LIMIT = 5

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

qwen2p5_3b = LocalModel(
    model="qwen2.5:3b",
    model_provider="ollama",
)

qwen2p5_7b = LocalModel(
    model="qwen2.5:7b",
    model_provider="ollama",
)

default_local_model = qwen2p5_7b


DATABASE_TYPE: SupportedDatabase = SupportedDatabase.IN_MEMORY
MODEL_NUM_CTX = 65536




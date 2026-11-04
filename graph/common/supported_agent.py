from enum import Enum


class SupportedAgent(str, Enum):
    """Supported database engine types for the application persistence layer."""
    PROOFREADER = "proofreader"
    SCORER = "scorer"
    EDITER = "editer"
    SUMMARIZER = "summarizer"
    CODER = "coder"
    INTENT_ANALYZER = "intent_analyzer"
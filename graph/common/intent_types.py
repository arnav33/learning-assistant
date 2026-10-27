from enum import Enum


class IntentType(str, Enum):
    CODE = "code"
    COMPACT = "compact"
    DETAILED = "detailed"
    REFERENCE = "reference"
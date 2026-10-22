from typing import Annotated, NotRequired

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class ChatState(TypedDict):
    topic: str
    query: str
    messages: Annotated[list, add_messages]
    results: NotRequired[list[dict]]
    compact: NotRequired[str]
    detailed: NotRequired[str]

from dataclasses import field
from typing import Annotated, Any

from langchain.agents import AgentState
from langgraph.graph.message import add_messages

from graph.common import IntentType


class ChatState(AgentState):
    topic: str = ""
    query: str = ""
    messages: Annotated[list, add_messages]
    results: list[dict] | None = None
    compact: str | None = None
    detailed: str | None = None
    references: list[str] | None = None
    codes: list[str] | None = None
    intents: list[IntentType] | None = None


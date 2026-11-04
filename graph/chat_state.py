from dataclasses import field
from typing import Annotated, Any

from langchain.agents import AgentState
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from graph.common import IntentType


class ChatState(AgentState):
    query: str = ""
    messages: list[BaseMessage] = []
    search_results: list[dict] | None = None
    browse_responses: list[dict] | None = None
    best_text: str | None = None
    best_codes: str | None = None
    codes: str | None = None
    compact: str | None = None
    detailed: str | None = None
    references: list[str] | None = None
    intents: list[IntentType] | None = None


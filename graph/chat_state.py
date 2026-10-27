from dataclasses import field
from typing import Annotated, Any

from langchain.agents import AgentState
from langgraph.graph.message import add_messages


class ChatState(AgentState):
    topic: str = ""
    query: str = ""
    messages: Annotated[list, add_messages]
    results: list[dict] | None = None
    compact: str | None = None
    detailed: str | None = None
    references: list[str] | None = None

    def get_property(self, name: str) -> Any:
        if name not in self.__dataclass_fields__:
            raise AttributeError(name)
        return getattr(self, name)

    def set_property(self, name: str, value: Any) -> dict[str, Any]:
        if name not in self.__dataclass_fields__:
            raise AttributeError(name)
        setattr(self, name, value)
        return {name: value}

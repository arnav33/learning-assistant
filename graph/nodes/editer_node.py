from typing import TypedDict

from aop import log_execution
from graph.agents import editer_agent
from graph.common import stream
from graph.templates import EDITER_TEMPLATE


class EditState(TypedDict):
    query: str
    best_text: str


@log_execution
def editer_node(state: EditState) -> dict:
    query, best_text = state["query"], state["best_text"]
    message = EDITER_TEMPLATE.format(query=query, data=best_text)
    detailed = stream(editer_agent, message)
    return {"detailed": detailed}

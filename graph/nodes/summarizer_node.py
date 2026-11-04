from typing import TypedDict

from aop import log_execution
from graph.agents import summarizer_agent
from graph.common import stream
from graph.templates import SUMMARIZER_TEMPLATE


class SummarizeState(TypedDict):
    query: str
    best_text: str


@log_execution
def summarizer_node(state: SummarizeState) -> dict:
    query, best_text = state["query"], state["best_text"]
    message = SUMMARIZER_TEMPLATE.format(query=query, data=best_text)
    compact = stream(summarizer_agent, message)
    return {"compact": compact}

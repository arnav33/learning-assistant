from typing import TypedDict

from aop import log_execution
from graph.agents import proofreader_agent
from graph.common import stream
from graph.templates import PROOFREADER_TEMPLATE


class QueryState(TypedDict):
    query: str


@log_execution
def proofread_query_node(state: QueryState) -> dict:
    query = state["query"]
    message = PROOFREADER_TEMPLATE.format(query=query)
    query = stream(proofreader_agent, message)
    print(f"PROOFREADER_QUERY::{query}")
    return {"query": query}

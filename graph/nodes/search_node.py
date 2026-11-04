from typing import TypedDict
from aop import log_execution
from graph.actions import search_action


class SearchState(TypedDict):
    query: str

@log_execution
def search_node(state: SearchState) -> dict:
    query = state["query"]
    search_results = search_action(query)
    return {"search_results": search_results}
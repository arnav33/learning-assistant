from typing import TypedDict
from aop import log_execution
from graph.actions import filter_action


class FilterState(TypedDict):
    search_results: list[dict]

@log_execution
def filter_node(state: FilterState) -> dict:
    search_results = state["search_results"]
    search_results = filter_action(search_results)
    return {"search_results": search_results}
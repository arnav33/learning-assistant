from typing import TypedDict
from aop import log_execution
from graph.actions import browse_action


class BrowseState(TypedDict):
    search_results: list[dict]

@log_execution
def browser_node(state: BrowseState) -> dict:
    search_results = state["search_results"]
    browse_responses = browse_action(search_results)
    return {"browse_responses": browse_responses,}
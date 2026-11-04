from typing import TypedDict
from aop import log_execution
from graph.actions import reference_action

class ReferenceState(TypedDict):
    search_results: list[dict]

@log_execution
def reference_node(state: ReferenceState) -> dict:
    search_results = state["search_results"]
    references = reference_action(search_results)
    return {"references": references}
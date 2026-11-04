from typing import TypedDict

from aop import log_execution
from graph.actions import rerank_action


class RerankState(TypedDict):
    query: str
    search_results: list[dict]


@log_execution
def rerank_node(state: RerankState) -> dict:
    query, search_results = state["query"], state["search_results"]
    search_results = rerank_action(query, search_results)
    return {"search_results": search_results}

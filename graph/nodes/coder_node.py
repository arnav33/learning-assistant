from typing import TypedDict
from aop import log_execution
from graph.agents import coder_agent
from graph.common import stream
from graph.templates import CODER_TEMPLATE


class CodeState(TypedDict):
    query: str
    best_codes: list[str]

@log_execution
def coder_node(state: CodeState) -> dict:
    query, best_codes = state["query"], state["best_codes"]
    message = CODER_TEMPLATE.format(browse_text=best_codes, query=query)
    codes = stream(coder_agent, message)
    return {"codes": codes}
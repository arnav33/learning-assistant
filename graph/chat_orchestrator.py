from langgraph.graph import END, START

from graph.chat_state import ChatState
from graph.common import IntentType, GraphBuilder
from graph.nodes import (
    best_codes_finder_node,
    best_text_finder_node,
    browser_node,
    coder_node,
    editer_node,
    filter_node,
    intent_analyzer_node,
    proofread_query_node,
    reference_node,
    rerank_node,
    search_node,
    summarizer_node,
)

from aop import log_execution, print_timers

_graph = None


@log_execution
def check_intents(state: ChatState,) -> dict:
    return [intent.value for intent in state["intents"]]


@log_execution
def route_after_best_text(state: ChatState) -> list[str]:
    return [
        intent.value
        for intent in state["intents"]
        if intent.value in (IntentType.COMPACT.value, IntentType.DETAILED.value)
    ]


@log_execution
def _orchestrator():
    nodes = [
        proofread_query_node,
        intent_analyzer_node,
        search_node,
        rerank_node,
        filter_node,
        reference_node,
        browser_node,
        best_codes_finder_node,
        best_text_finder_node,
        coder_node,
        editer_node,
        summarizer_node,
    ]

    edges = [
        (START, proofread_query_node),
        (proofread_query_node, intent_analyzer_node),
        (intent_analyzer_node, search_node),
        (search_node, rerank_node),
        (rerank_node, filter_node),
        (filter_node, browser_node),
        (best_codes_finder_node, coder_node),
        (coder_node, END),
        (summarizer_node, END),
        (editer_node, END),
        (reference_node, END),
    ]

    conditional_edges = [
        (browser_node, check_intents, [
            (IntentType.CODE, best_codes_finder_node),
            (IntentType.COMPACT, best_text_finder_node),
            (IntentType.DETAILED, best_text_finder_node),
            (IntentType.REFERENCE, reference_node),
        ]),
        (best_text_finder_node, route_after_best_text, [
            (IntentType.COMPACT, summarizer_node),
            (IntentType.DETAILED, editer_node),
        ]),
    ]

    global _graph
    if _graph is None:
        _graph = (
            GraphBuilder.builder()
            .name("chat_orchestrator")
            .state(ChatState)
            .nodes(nodes)
            .edges(edges)
            .conditional_edges(conditional_edges)
            .build()
        )
    return _graph


@print_timers
def orchestrate(query: str):
    state: ChatState = {"query": query}
    result = _orchestrator().invoke(state)
    compact = result["compact"] if "compact" in result else None
    detailed = result["detailed"] if "detailed" in result else None
    references = result["references"] if "references" in result else None
    codes = result["codes"] if "codes" in result else None
    return compact, detailed, references, codes

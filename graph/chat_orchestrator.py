from langchain.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from graph.common.chat_state import ChatState
from graph.nodes.agents import intent_analyzer_agent, proofreader_agent, editer_agent, summarizer_agent, coder_agent
from graph.nodes.actions import filter_action, reference_action, rerank_action, search_action
from graph.templates import CODER_TEMPLATE, EDITER_TEMPLATE, INTENT_ANALYZER_TEMPLATE, SUMMARIZER_TEMPLATE, PROOFREADER_TEMPLATE
from graph.common import IntentType, invoke

from aop import log_execution, print_timers

_graph = None


@log_execution
def check_intents(state: ChatState,) -> dict:
    return [intent.value for intent in state["intents"]]
    

@log_execution
def proofread_query(state: ChatState) -> dict:
    topic, query = state["topic"], state["query"]
    message = PROOFREADER_TEMPLATE.format(topic=topic, query=query)
    query = invoke(proofreader_agent, message)
    return {"query": query}


@log_execution
def intent_analysis(state: ChatState) -> dict:
    query, topic = state["query"], state["topic"]
    intent_types = [intent.value for intent in IntentType]
    message = INTENT_ANALYZER_TEMPLATE.format(
        query=query,
        topic=topic,
        IntentType=intent_types,
    )
    response = intent_analyzer_agent.invoke({
        "messages": [HumanMessage(content=message)],
    })
    intents = response["structured_response"].intent_types
    return {"intents": intents}


@log_execution
def search(state: ChatState) -> dict:
    query = state["query"]
    results = search_action(query)
    return {"results": results}


@log_execution
def rerank(state: ChatState) -> dict:
    query, results = state["query"], state["results"]
    results = rerank_action(query, results)
    return {"results": results}


@log_execution
def filter(state: ChatState) -> dict:
    results = state["results"]
    results = filter_action(results)
    return {"results": results}


@log_execution
def reference(state: ChatState) -> dict:
    results = state["results"]
    references = reference_action(results)
    return {"references": references}


@log_execution
def code(state: ChatState) -> dict:
    query, results = state["query"], state["results"]
    message = CODER_TEMPLATE.format(results=results, query=query)
    codes = invoke(coder_agent, message)
    return {"codes": codes}


@log_execution
def edit(state: ChatState) -> dict:
    query, results = state["query"], state["results"]
    message = EDITER_TEMPLATE.format(query=query, results=results)
    detailed = invoke(editer_agent, message)
    return {"detailed": detailed}


@log_execution
def summarize(state: ChatState) -> dict:
    query, results = state["query"], state["results"]
    message = SUMMARIZER_TEMPLATE.format(query=query, results=results)
    compact = invoke(summarizer_agent, message)
    return {"compact": compact}


@log_execution
def _orchestrator():
    graph = StateGraph(ChatState)

    graph.add_node("proofread_query", proofread_query)
    graph.add_node("intent_analysis", intent_analysis)
    graph.add_node("search", search)
    graph.add_node("rerank", rerank)
    graph.add_node("filter", filter)
    graph.add_node("reference", reference)
    graph.add_node("code", code)
    graph.add_node("edit", edit)
    graph.add_node("summarize", summarize)
    
    graph.add_edge(START, "proofread_query")
    graph.add_edge("proofread_query", "intent_analysis")
    graph.add_edge("intent_analysis", "search")
    graph.add_edge("search", "rerank")
    graph.add_edge("rerank", "filter")
    graph.add_conditional_edges("filter", check_intents, {
        "code": "code",
        "compact": "summarize",
        "detailed": "edit",
        "reference": "reference",
    })
    graph.add_edge("code", END)
    graph.add_edge("summarize", END)
    graph.add_edge("edit", END)
    graph.add_edge("reference", END)
    
    return graph.compile()


@print_timers
def orchestrate(query: str, topic: str):
    global _graph
    _graph = _graph or _orchestrator()
    state: ChatState = {"query": query, "topic": topic}
    result = _graph.invoke(state)
    compact = result["compact"] if "compact" in result else None
    detailed = result["detailed"] if "detailed" in result else None
    references = result["references"] if "references" in result else None
    codes = result["codes"] if "codes" in result else None
    return compact, detailed, references, codes


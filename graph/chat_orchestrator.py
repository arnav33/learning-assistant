from langchain.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from graph.chat_state import ChatState
from graph.nodes.agents import proofreader_agent, editer_agent, summarizer_agent
from graph.nodes.actions import filter_action, reference_action, rerank_action, search_action
from graph.templates import proofreader_template, summarizer_template, editer_template
from graph.common import invoke

from aop import log_execution, print_timers

_graph = None


@log_execution
def proofread_query(state: ChatState) -> dict:
    topic, query = state["topic"], state["query"]
    message = proofreader_template().format(topic=topic, query=query)
    query = invoke(proofreader_agent, message)
    print(query)
    return {"query": query}


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
def edit(state: ChatState) -> dict:
    query, results = state["query"], state["results"]
    message = editer_template().format(query=query, results=results)
    detailed = invoke(editer_agent, message)
    print(detailed)
    return {"detailed": detailed}


@log_execution
def summarizer(state: ChatState) -> dict:
    query, detailed = state["query"], state["detailed"]
    message = summarizer_template().format(query=query, detailed=detailed)
    compact = invoke(summarizer_agent, message)
    return {"compact": compact}


@log_execution
def _orchestrator():
    graph = StateGraph(ChatState)
    graph.add_node("proofread_query", proofread_query)
    graph.add_node("search", search)
    graph.add_node("rerank", rerank)
    graph.add_node("filter", filter)
    graph.add_node("reference", reference)
    graph.add_node("edit", edit)
    graph.add_node("summarizer", summarizer)
    graph.add_edge(START, "proofread_query")
    graph.add_edge("proofread_query", "search")
    graph.add_edge("search", "rerank")
    graph.add_edge("rerank", "filter")
    graph.add_edge("filter", "reference")
    graph.add_edge("reference", "edit")
    graph.add_edge("edit", "summarizer")
    graph.add_edge("summarizer", END)
    return graph.compile()


@print_timers
def orchestrate(query: str, topic: str):
    global _graph
    _graph = _graph or _orchestrator()
    state: ChatState = {"query": query, "topic": topic}
    result = _graph.invoke(state)
    return (result["compact"], result["detailed"], result["references"])


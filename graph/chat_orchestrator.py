from langchain.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from graph.agents.formatter_agent import formatter_agent
from graph.agents.synthesizer_agent import synthesizer_agent
from graph.chat_state import ChatState
from graph.utils.search_node import search_node
from graph.utils.whois_node import whois_node


def search(state: ChatState) -> dict:
    response = search_node(state["query"])
    results = whois_node(response.get("results") or [])
    error = response.get("error")
    update: dict = {"results": results}
    if error or not results:
        update["messages"] = [AIMessage(content=error or "No results found.")]
    return update


def synthesize(state: ChatState) -> dict:
    results = state.get("results") or []
    if not results:
        return {}
    blocks = []
    links = []
    for item in results:
        title = str(item.get("title") or "").replace("[", "").replace("]", "").strip()
        href = str(item.get("href") or "").strip()
        body = str(item.get("body") or "").strip()
        blocks.append(f"title: {title}\nhref: {href}\nbody: {body}")
        if title and href.startswith("http"):
            links.append(f"[{title}]({href})")
    result = synthesizer_agent.invoke({
        "messages": [HumanMessage(content=(
            f"Question: {state['query']}\n\n"
            f"Sources:\n\n" + "\n\n".join(blocks) + "\n\n"
            f"End the answer with these lines:\n" + "\n".join(links)
        ))],
    })
    text = _message_text(result).strip() or "The reply failed."
    return {"detailed": text}


def formatter(state: ChatState) -> dict:
    detailed = state.get("detailed") or ""
    if not detailed:
        return {}
    query = state.get("query") or ""
    message = f"Query: {query}, Answer: {detailed}"
    result = formatter_agent.invoke({
        "messages": [HumanMessage(content=message)],
    })
    compact = _message_text(result).strip()
    update: dict = {}
    if compact:
        update["compact"] = compact
    linked = _with_source_links(detailed, state.get("results") or [])
    if linked != detailed:
        update["detailed"] = linked
    return update


def _orchestrator():
    graph = StateGraph(ChatState)
    graph.add_node("search", search)
    graph.add_node("synthesize", synthesize)
    graph.add_node("formatter", formatter)
    graph.add_edge(START, "search")
    graph.add_edge("search", "synthesize")
    graph.add_edge("synthesize", "formatter")
    graph.add_edge("formatter", END)
    return graph.compile()


_graph = None

def _get_graph():
    global _graph
    _graph = _graph if _graph else _orchestrator()
    return _graph


def orchestrate(query: str, topic: str) -> tuple[str, str | None, str | None, list[dict] | None, bool]:
    try:
        result = _get_graph().invoke({
            "query": query,
            "topic": topic,
            "messages": [HumanMessage(content=query)],
        })
    except Exception as exc:
        return str(exc), None, None, None, False
    messages = result.get("messages") or []
    content = messages[-1].content if messages else ""
    content = content if isinstance(content, str) else str(content)
    compact = result.get("compact") or ""
    detailed = result.get("detailed") or ""
    reply = compact or detailed or content or "The reply failed."
    results = result.get("results")
    succeeded = bool(compact or detailed)
    return reply, compact or None, detailed or None, results if isinstance(results, list) else None, succeeded


def _with_source_links(text: str, results: list[dict]) -> str:
    links = []
    for item in results:
        title = str(item.get("title") or "").replace("[", "").replace("]", "").strip()
        href = str(item.get("href") or "").strip()
        if title and href.startswith("http"):
            links.append(f"[{title}]({href})")
    missing = [link for link in links if link not in text]
    if not text or not missing:
        return text
    return text.rstrip() + "\n\n" + "\n".join(missing)


def _message_text(result: dict) -> str:
    messages = result.get("messages") or []
    content = messages[-1].content if messages else result.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(str(block.get("text") or ""))
        return "".join(parts)
    return ""

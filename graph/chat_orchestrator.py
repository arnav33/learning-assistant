import json
import logging

from langchain.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from graph.agents.formatter_agent import formatter_agent
from graph.agents.synthesizer_agent import synthesizer_agent
from graph.chat_state import ChatState

logger = logging.getLogger("uvicorn.error")


def synthesize(state: ChatState) -> dict:
    result = synthesizer_agent.invoke({
        "messages": [HumanMessage(content=f"Question: {state['query']}")],
    })
    text = _message_text(result).strip() or "The reply failed."
    update: dict = {"detailed": text}
    results = _tool_results(result)
    if results:
        update["results"] = results
    return update


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
    graph.add_node("synthesize", synthesize)
    graph.add_node("formatter", formatter)
    graph.add_edge(START, "synthesize")
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


def _tool_results(result: dict) -> list[dict]:
    found: list[dict] = []
    ages: dict[str, object] = {}
    for message in result.get("messages") or []:
        name = getattr(message, "name", None)
        content = getattr(message, "content", None)
        if not isinstance(content, str):
            continue
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            continue
        if name == "search_tool" and isinstance(payload, dict):
            found = [item for item in payload.get("results") or [] if isinstance(item, dict)]
        elif name == "whois_tool" and isinstance(payload, list):
            aged = [item for item in payload if isinstance(item, dict)]
            if any(item.get("title") for item in aged):
                found = aged
            else:
                for item in aged:
                    if item.get("href"):
                        ages[str(item["href"])] = item.get("age")
        elif name == "filter_tool" and isinstance(payload, list):
            found = [item for item in payload if isinstance(item, dict)]
    if ages and found:
        found = [
            {**item, "age": ages.get(str(item.get("href") or ""), item.get("age"))}
            for item in found
        ]
    logger.info("chat final result count: %s", len(found))
    return found


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

import json
import logging
import re

from langchain.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from graph.agents.query_agent import query_agent
from graph.agents.synthesizer_agent import synthesizer_agent
from graph.agents.formatter_agent import formatter_agent
from graph.chat_state import ChatState


def optimize_query(state: ChatState) -> dict:
    query = state.get("query") or ""
    result = query_agent.invoke({
        "messages": [HumanMessage(content=query)],
    })
    optimized = _message_text(result).strip() or query
    print(f"Optimized query: {optimized}")
    return {"query": optimized}


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
    raw = state.get("detailed") or ""
    if not raw:
        return {}
    references = _references(raw, state.get("results") or [])
    detailed = _clean_detailed(raw, references)
    query = state.get("query") or ""
    message = f"Query: {query}, Answer: {detailed}"
    result = formatter_agent.invoke({
        "messages": [HumanMessage(content=message)],
    })
    compact = _message_text(result).strip()
    update: dict = {"detailed": detailed}
    if compact:
        update["compact"] = compact
    if references:
        update["references"] = references
    return update


def _orchestrator():
    graph = StateGraph(ChatState)
    graph.add_node("optimize_query", optimize_query)
    graph.add_node("synthesize", synthesize)
    graph.add_node("formatter", formatter)
    graph.add_edge(START, "optimize_query")
    graph.add_edge("optimize_query", "synthesize")
    graph.add_edge("synthesize", "formatter")
    graph.add_edge("formatter", END)
    return graph.compile()


_graph = None

def _get_graph():
    global _graph
    _graph = _graph if _graph else _orchestrator()
    return _graph


def orchestrate(query: str, topic: str) -> tuple[str, str | None, str | None, list[dict] | None, list[str] | None, bool]:
    try:
        result = _get_graph().invoke({
            "query": query,
            "topic": topic,
            "messages": [HumanMessage(content=query)],
        })
    except Exception as exc:
        return str(exc), None, None, None, None, False
    messages = result.get("messages") or []
    content = messages[-1].content if messages else ""
    content = content if isinstance(content, str) else str(content)
    compact = result.get("compact") or ""
    detailed = result.get("detailed") or ""
    reply = compact or detailed or content or "The reply failed."
    results = result.get("results")
    references = result.get("references") or []
    succeeded = bool(compact or detailed)
    return (
        reply,
        compact or None,
        detailed or None,
        results if isinstance(results, list) else None,
        references if isinstance(references, list) and references else None,
        succeeded,
    )


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
    return found


_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")
_INSTRUCTION = "end the answer with these lines:"


def _references(text: str, results: list[dict]) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    for item in results:
        title = str(item.get("title") or "").replace("[", "").replace("]", "").strip()
        href = str(item.get("href") or "").strip()
        if title and href.startswith("http") and href not in seen:
            links.append(f"[{title}]({href})")
            seen.add(href)
    for match in _LINK.finditer(text):
        href = match.group(2)
        if href not in seen:
            links.append(match.group(0))
            seen.add(href)
    return links


def _clean_detailed(text: str, references: list[str]) -> str:
    titles = {match.group(1).strip() for link in references if (match := _LINK.fullmatch(link.strip()))}
    lines = []
    for line in _LINK.sub("", text).splitlines():
        plain = _line_text(line)
        if plain.lower() == _INSTRUCTION or plain in titles:
            continue
        lines.append(line.rstrip())
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return cleaned or text.strip()


def _line_text(line: str) -> str:
    text = line.strip()
    text = re.sub(r"^(?:[-*•]|\d+[.)])\s+", "", text)
    text = text.replace("**", "").replace("__", "").strip("*_` ")
    return text.strip()


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

import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, ToolMessage

from backend.service.agent_service import agent_service
from backend.service.model_service import model_service
from config import SupportedAgent
from graph.tools.filter_tool import filter_tool
from graph.tools.search_tool import search_tool
from graph.tools.whois_tool import whois_tool
from prompts.synthesizer_prompt import synthesizer_prompt

_synthesis_agent = agent_service.get_by_name(SupportedAgent.SYNTHESIS)
_synthesis_model = model_service.get_by_id(_synthesis_agent.model_id)

_writer = create_agent(
    model=init_chat_model(**_synthesis_model.to_dict()),
    system_prompt=synthesizer_prompt(_synthesis_agent.performance_reviews),
)


class _Synthesizer:
    """Runs search, whois, and filter, then writes from the kept sources."""

    def invoke(self, payload: dict) -> dict:
        question = _question(payload)
        searched = search_tool.invoke({"query": question})
        results = searched.get("results") or [] if isinstance(searched, dict) else []
        aged = whois_tool.invoke({"results": results}) if results else []
        kept = filter_tool.invoke({"results": aged}) if aged else []
        written = _writer.invoke({
            "messages": [HumanMessage(content=_brief(question, kept))],
        })
        tool_messages = [
            _tool_message("search_tool", searched, "search"),
            _tool_message("whois_tool", aged, "whois"),
            _tool_message("filter_tool", kept, "filter"),
        ]
        return {"messages": tool_messages + (written.get("messages") or [])}


def _question(payload: dict) -> str:
    messages = payload.get("messages") or []
    content = messages[-1].content if messages else ""
    text = content if isinstance(content, str) else str(content)
    prefix = "Question: "
    if text.startswith(prefix):
        return text[len(prefix):].strip()
    return text.strip()


def _brief(question: str, results: list[dict]) -> str:
    blocks = []
    links = []
    for item in results:
        title = str(item.get("title") or "").replace("[", "").replace("]", "").strip()
        href = str(item.get("href") or "").strip()
        body = str(item.get("body") or "").strip()
        blocks.append(f"title: {title}\nhref: {href}\nbody: {body}")
        if title and href.startswith("http"):
            links.append(f"[{title}]({href})")
    return (
        f"Question: {question}\n\n"
        f"Sources:\n\n" + "\n\n".join(blocks) + "\n\n"
        f"End the answer with these lines:\n" + "\n".join(links)
    )


def _tool_message(name: str, payload: object, call_id: str) -> ToolMessage:
    return ToolMessage(content=json.dumps(payload), name=name, tool_call_id=call_id)


synthesizer_agent = _Synthesizer()

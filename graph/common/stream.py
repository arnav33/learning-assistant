from typing import Any

from langchain.messages import HumanMessage


def stream(agent: Any, message: str) -> str:
    """
    Streams text tokens from the agent silently in memory
    and returns the fully aggregated string payload.
    """
    parts: list[str] = []
    last_text = ""
    try:
        for mode, data in agent.stream(
            {"messages": [HumanMessage(content=message)]},
            stream_mode=["messages", "values"],
        ):
            if mode == "messages":
                token = data[0] if isinstance(data, tuple) else data
                if getattr(token, "type", None) not in {"ai", "AIMessageChunk"}:
                    continue
                parts.append(str(token.text))
            elif mode == "values" and isinstance(data, dict):
                messages = data.get("messages") or []
                if messages and getattr(messages[-1], "type", None) == "ai":
                    last_text = str(messages[-1].text).strip()
    except Exception as e:
        print(f"Error streaming: {e}")

    result = "".join(parts).strip() or last_text or "The reply failed."
    print(f"STREAM_RESULT::{result}")
    return result

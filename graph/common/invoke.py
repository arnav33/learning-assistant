from typing import Any

from langchain_core.messages import HumanMessage


def invoke(agent, message: str) -> Any:
    result = agent.invoke({
        "messages": [HumanMessage(content=message)],
    })
    print(f"INVOKE_RESULT::{result}")
    if isinstance(result, dict) and "messages" in result:
        return result["messages"][-1].text.strip() or "The reply failed."
    return result

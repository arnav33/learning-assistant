


from langchain_core.messages import HumanMessage


def invoke(agent, message: str) -> str:
    result = agent.invoke({
        "messages": [HumanMessage(content=message)],
    })
    return result["messages"][-1].text.strip() or "The reply failed."
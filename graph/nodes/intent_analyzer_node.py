from typing import TypedDict
from langchain_core.messages import HumanMessage
from aop import log_execution
from graph.agents import intent_analyzer_agent
from graph.common import IntentType
from graph.templates import INTENT_ANALYZER_TEMPLATE


class IntentAnalysisState(TypedDict):
    query: str


@log_execution
def intent_analyzer_node(state: IntentAnalysisState) -> dict:
    query = state["query"]
    intent_types = [intent.value for intent in IntentType]
    message = INTENT_ANALYZER_TEMPLATE.format(
        query=query,
        IntentType=intent_types,
    )
    response = intent_analyzer_agent.invoke({
        "messages": [HumanMessage(content=message)],
    })
    intents = response["structured_response"].intent_types
    print(f"INTENTS::{intents}")
    return {"intents": intents}
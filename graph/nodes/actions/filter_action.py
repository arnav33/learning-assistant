import json
from typing import Annotated

from langchain.messages import ToolMessage
from langchain.tools import InjectedState, InjectedToolCallId, tool
from langgraph.types import Command

from config import ToolConfig

OLDEST_RESULT_LIMIT = int(ToolConfig.OLDEST_RESULT_LIMIT)


def filter_action(results: list[dict]) -> Command | str:
    """Keep the top reranked pages.

    Call this after rerank_tool. The pages come from that rerank, in that order.
    """
    return [{**item, "rank": index} for index, item in enumerate(results[:OLDEST_RESULT_LIMIT], start=1)]

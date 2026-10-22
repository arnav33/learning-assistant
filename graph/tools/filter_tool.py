import logging

from langchain.tools import tool

from config import ToolConfig

OLDEST_RESULT_LIMIT = int(ToolConfig.OLDEST_RESULT_LIMIT)

logger = logging.getLogger("uvicorn.error")


@tool
def filter_tool(results: list[dict]) -> list[dict]:
    """Rerank pages by domain age and keep the oldest ones.

    The oldest domain gets rank 1. The newest domain gets the last rank.
    Pages with no age are ranked after the dated pages.
    """
    dated = []
    undated = []
    for item in results:
        if _age(item) is None:
            undated.append(item)
        else:
            dated.append(item)
    dated.sort(key=_age, reverse=True)
    kept = (dated + undated)[:OLDEST_RESULT_LIMIT]
    ranked = [{**item, "rank": index} for index, item in enumerate(kept, start=1)]
    logger.info("filter_tool final result count: %s", len(ranked))
    return ranked


def _age(item: dict) -> int | None:
    age = item.get("age")
    if isinstance(age, bool) or not isinstance(age, (int, float)):
        return None
    return int(age)

from ddgs import DDGS

from config import ToolConfig

PAGE_SIZE = int(ToolConfig.PAGE_SIZE)


def search_action(query: str) -> list[dict]:
    return DDGS(timeout=20).text(
        query.strip(),
        max_results=PAGE_SIZE,
        backend="duckduckgo,bing,yahoo",
    )

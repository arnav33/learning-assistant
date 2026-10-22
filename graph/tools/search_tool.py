import threading
import time

from ddgs import DDGS
from ddgs.exceptions import DDGSException
from langchain.tools import tool

from config import ToolConfig

PAGE_SIZE = int(ToolConfig.PAGE_SIZE)

page = 1
_current_query = ""
_lock = threading.Lock()


@tool
def search_tool(query: str) -> dict:
    """Search the web for this query and return one page of at most 10 results.

    page starts at 1 for each query. After that query returns results, page moves
    forward so the next call for the same query fetches the next 10. A different
    query starts again at page 1.
    """
    global page, _current_query
    text = query.strip()
    if not text:
        return {"results": [], "error": "A search query is required."}

    with _lock:
        if text != _current_query:
            _current_query = text
            page = 1
        page_number = page

    try:
        batch = _fetch(text, page_number)
    except DDGSException as exc:
        return {"results": [], "error": str(exc)}

    if not batch:
        return {"results": []}

    start = (page_number - 1) * PAGE_SIZE
    results = [
        {"rank": start + index + 1, **item}
        for index, item in enumerate(batch[:PAGE_SIZE])
    ]
    with _lock:
        if _current_query == text and page == page_number:
            page += 1
    return {"results": results}


def _fetch(query: str, page_number: int) -> list[dict]:
    last_error: DDGSException | None = None
    for attempt in range(2):
        try:
            return DDGS(timeout=20).text(
                query,
                max_results=PAGE_SIZE,
                page=page_number,
                backend="duckduckgo,bing,yahoo",
            ) or []
        except DDGSException as exc:
            last_error = exc
            if "No results found" not in str(exc) or attempt == 1:
                break
            time.sleep(1)
    if last_error and page_number == 1:
        raise last_error
    return []



def rerank_action(query: str, results: list[dict]) -> list[dict]:
    """Move official documentation pages to the front of the search results.

    Call this after search_tool with the same query. The pages come from that
    search. The first official result becomes rank 1, the second becomes rank 2,
    and each following official result takes the next rank. Every other result
    shifts down.
    """
    hosts = official_hosts(query, results)
    return _promote(results, hosts) if hosts else results


def _promote(results: list[dict], hosts: set[str]) -> list[dict]:
    official = []
    rest = []
    for item in results:
        found = host(str(item.get("href") or ""))
        if found and any(same_site(found, official_host) for official_host in hosts):
            official.append(item)
        else:
            rest.append(item)
    return [{**item, "rank": index} for index, item in enumerate(official + rest, start=1)]


import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

_LOOKUP_SECONDS = 2
_PYPI = "https://pypi.org/pypi/{name}/json"
_FORGES = {"github.com", "gitlab.com", "bitbucket.org", "pypi.org", "npmjs.com"}
_STOP = {
    "what", "is", "the", "a", "an", "how", "do", "does", "can", "i", "for", "in",
    "of", "to", "and", "or", "on", "with", "about", "latest", "syntax", "creating",
    "create", "write", "using", "use", "from", "this", "that", "are", "be", "it",
}


def official_hosts(query: str, results: list[dict]) -> set[str]:
    result_hosts = [found for item in results if (found := host(str(item.get("href") or "")))]
    best: set[str] = set()
    best_count = 0
    for name in _candidates(query):
        hosts = _fetch_hosts(name) or set()
        count = sum(1 for page in result_hosts if any(same_site(page, official) for official in hosts))
        if count > best_count:
            best = hosts
            best_count = count
    return best


def same_site(host: str, official: str) -> bool:
    return host == official or host.endswith("." + official)


def _candidates(query: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for token in re.findall(r"[A-Za-z0-9]+", query):
        name = token.lower()
        if len(name) < 3 or name in _STOP or name in seen:
            continue
        seen.add(name)
        names.append(name)
    names.sort(key=len, reverse=True)
    return names[:6]


def _fetch_hosts(name: str) -> set[str] | None:
    request = Request(_PYPI.format(name=name), headers={"User-Agent": "learning-assistant"})
    try:
        with urlopen(request, timeout=_LOOKUP_SECONDS) as response:
            payload = json.load(response)
    except HTTPError as exc:
        return set() if exc.code == 404 else None
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None
    info = payload.get("info") if isinstance(payload, dict) else None
    if not isinstance(info, dict):
        return set()
    urls: list[str] = []
    home = info.get("home_page")
    if isinstance(home, str):
        urls.append(home)
    project_urls = info.get("project_urls") or {}
    if isinstance(project_urls, dict):
        for label, url in project_urls.items():
            if isinstance(label, str) and isinstance(url, str) and _is_official_label(label):
                urls.append(url)
    return {found for url in urls if (found := host(url)) and found not in _FORGES}


def _is_official_label(label: str) -> bool:
    text = label.lower()
    return "doc" in text or "home" in text or "official" in text


def host(url: str) -> str | None:
    hostname = urlparse(url).hostname
    if not hostname:
        return None
    host = hostname.lower()
    if host.startswith("www."):
        host = host[4:]
    return host
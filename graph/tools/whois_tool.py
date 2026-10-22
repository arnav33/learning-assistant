import threading
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime, timezone
from urllib.parse import urlparse

from langchain.tools import tool
from whois import WhoisError, extract_domain, whois

_lock = threading.Lock()
_ages: dict[str, int | None] = {}
_LOOKUP_SECONDS = 4


@tool
def whois_tool(results: list[dict]) -> list[dict]:
    """Add the domain age, in days, to each search result.

    age is the number of days since the domain was registered. It is None when
    the registration date cannot be read.
    """
    domains = [_domain(item.get("href") or "") for item in results]
    _fill([domain for domain in dict.fromkeys(domains) if domain])
    with _lock:
        ages = {domain: _ages.get(domain) for domain in domains if domain}
    return [{**item, "age": ages.get(domain)} for item, domain in zip(results, domains)]


def _fill(domains: list[str]) -> None:
    with _lock:
        missing = [domain for domain in domains if domain not in _ages]
    if not missing:
        return
    pool = ThreadPoolExecutor(max_workers=min(8, len(missing)))
    futures = [pool.submit(_lookup, domain) for domain in missing]
    _, pending = wait(futures, timeout=_LOOKUP_SECONDS)
    for future in pending:
        future.cancel()
    pool.shutdown(wait=False, cancel_futures=True)


def _domain(href: str) -> str | None:
    if not href:
        return None
    try:
        return extract_domain(href)
    except Exception:
        host = urlparse(href).hostname
        return host.lower() if host else None


def _lookup(domain: str) -> int | None:
    try:
        record = whois(domain, timeout=3, quiet=True)
        created = _earliest(record.get("creation_date"))
    except (WhoisError, OSError, ValueError):
        age = None
    else:
        age = _days(created)
    with _lock:
        _ages.setdefault(domain, age)
    return age


def _days(created: datetime | None) -> int | None:
    if created is None:
        return None
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    days = (datetime.now(timezone.utc) - created).days
    return days if days >= 0 else None


def _earliest(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, list):
        dates = [item for item in value if isinstance(item, datetime)]
        return min(dates) if dates else None
    return None

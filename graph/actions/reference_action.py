def reference_action(results: list[dict]) -> list[str]:
    """Save a reference for each kept page.

    Call this after filter_tool. The heading is the page title and the url is
    the page address.
    """
    references: list[str] = []
    seen: set[str] = set()
    for item in results:
        heading = str(item.get("title") or "").replace("[", "").replace("]", "").strip()
        url = str(item.get("href") or "").strip()
        if not heading or not url.startswith("http") or url in seen:
            continue
        seen.add(url)
        references.append(f"[{heading}]({url})")
    return references

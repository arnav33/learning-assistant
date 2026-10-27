def summarizer_template() -> str:
    return (
        "Write a short sentence to summarize contents in results: {results}, to answer the query: {query}"
    )

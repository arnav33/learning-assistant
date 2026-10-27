def editer_template() -> str:
    return (
        "Create 1-2 paragraphs to summarize {results}, to answer the query: {query}\n"
        "If it has code blocks, generate a code block that answers the query."
    )

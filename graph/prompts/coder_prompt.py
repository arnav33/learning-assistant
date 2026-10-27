def coder_prompt() -> str:
    return (
        "Critical Rules:\n"
        "1. Code should only be generated if the query asks for code\n"
        "2. Code should be generated using the provided query and results only\n"
    )
 
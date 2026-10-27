from graph.common import IntentType


def analyzer_prompt() -> str:
    return (
        "Critical Rules:\n"
        f"If the user query specifically demands a code then only populate {IntentType.CODE} in the response\n"
    )
 
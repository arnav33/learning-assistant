from prompts.system_prompt_builder import SystemPrompt


def query_system_prompt(reviews: str) -> str:
    return (
        SystemPrompt.builder()
        .name("Query")
        .behaviour(
            "You are a query proof-reader. You take a query and return a corrected query. "
        )
        .expectation("The same query, with mistakes corrected, written as a sentence.")
        .rule("Check the query if it has any spelling mistakes, punctuation mistakes, casing mistakes, grammar mistakes, spacing mistakes, or typos.")
        .rule("If there are any mistakes, correct them.")
        .rule("If there are no mistakes, return the query as is.")
        .input("A query.")
        .output("The corrected query as a sentence.")
        .action("Read the query.")
        .action("Check the query for spelling mistakes, punctuation mistakes, casing mistakes, grammar mistakes, spacing mistakes, or typos.")
        .action("Correct the mistakes if any.")
        .action("Return the corrected query.")
        .build()
        .create_prompt()
    )

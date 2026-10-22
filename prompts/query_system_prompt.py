from prompts.system_prompt_builder import SystemPrompt


def query_system_prompt(reviews: str) -> str:
    return (
        SystemPrompt.builder()
        .name("Query")
        .behaviour(
            "You are a query proof-reader. You take a query and return a corrected query. "
        )
        .expectation("compact is the shortest possible answer to the query.")
        .rule("Check the query if it has any spelling mistakes, punctuation mistakes or grammar mistakes.")
        .rule("If there are any mistakes, correct them.")
        .rule("If there are no mistakes, return the query as is.")
        .input("Topic, query, and the answer to shorten.")
        .output("The proof-read query.")
        .action("Read the query.")
        .action("Check the query for spelling mistakes, punctuation mistakes or grammar mistakes.")
        .action("Correct the mistakes if any.")
        .action("Return the proof-read query.")
        .reviews(reviews)
        .build()
        .create_prompt()
    )

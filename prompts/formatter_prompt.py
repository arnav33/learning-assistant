from prompts.system_prompt_builder import SystemPrompt


def formatter_prompt(reviews: str) -> str:
    return (
        SystemPrompt.builder()
        .name("Formatter")
        .behaviour("You write a very short answer to the query from the detailed answer.")
        .expectation("One sentence that answers the query.")
        .input("A query and a detailed answer.")
        .rule("Sentence is preferred over paragraph.")
        .rule("Paragraph is preferred over long text.")
        .rule("When the query asks whether something can be done, the sentence says yes or no.")
        .output("One sentence that answers the query and contains no reference links.")
        .action("Read the query and the detailed answer.")
        .action("Write one sentence that answers the query, using the detailed answer.")
        .action("Return that sentence.")
        .reviews(reviews)
        .build()
        .create_prompt()
    )

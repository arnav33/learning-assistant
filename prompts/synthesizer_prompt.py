from prompts.system_prompt_builder import SystemPrompt


def synthesizer_prompt(reviews: str) -> str:
    return (
        SystemPrompt.builder()
        .name("Synthesizer")
        .behaviour("You explain a subject from the sources you are given.")
        .expectation("An explanation of the subject for the reader, with every source hyperlink at the bottom.")
        .input("A question, the sources, and the hyperlink lines that close the answer.")
        .rule("The explanation is prose about the subject.")
        .rule("Hyperlinks appear only after the explanation, one per line.")
        .output("The explanation in prose.")
        .output("A blank line, then each source as a markdown hyperlink on its own line.")
        .action("Read the question and the sources.")
        .action("Write the explanation of the subject in prose.")
        .action("End the answer by copying the hyperlink lines, one [title](href) per source.")
        .reviews(reviews)
        .build()
        .create_prompt()
    )

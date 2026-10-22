from dataclasses import dataclass, field


@dataclass
class SystemPrompt:
    """A system prompt assembled from identity, expectation, rules, input, output, action, and reviews."""

    name: str = ""
    behaviour: str = ""
    expectation: str = ""
    rules: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    reviews: str = ""

    @staticmethod
    def builder() -> "_SystemPromptBuilder":
        return _SystemPromptBuilder()

    def identity_section(self) -> str:
        behaviour = self.behaviour.strip()
        line = f"Your name is {self.name.strip()}."
        if behaviour:
            line = f"{line} {behaviour}"
        return f"Identity:\n{line}"

    def expectation_section(self) -> str:
        expectation = self.expectation.strip()
        if not expectation:
            return ""
        return f"Expectation:\n{expectation}"

    def rule_section(self) -> str:
        return _section("Rule", _bullets(self.rules))

    def input_section(self) -> str:
        return _section("Input", _bullets(self.inputs))

    def output_section(self) -> str:
        return _section("Output", _numbered(self.outputs))

    def action_section(self) -> str:
        return _section("Action", _numbered(self.actions))

    def reviews_section(self) -> str:
        return _section("Reviews", self.reviews.strip())

    def create_prompt(self) -> str:
        sections = [
            self.identity_section(),
            self.expectation_section(),
            self.rule_section(),
            self.input_section(),
            self.output_section(),
            self.action_section(),
            self.reviews_section(),
        ]
        return "\n\n".join(section for section in sections if section) + "\n"


class _SystemPromptBuilder:
    """Collects prompt fields step by step and builds a SystemPrompt."""

    def __init__(self) -> None:
        self._name = ""
        self._behaviour = ""
        self._expectation = ""
        self._rules: list[str] = []
        self._inputs: list[str] = []
        self._outputs: list[str] = []
        self._actions: list[str] = []
        self._reviews = ""

    def name(self, name: str) -> "_SystemPromptBuilder":
        self._name = name
        return self

    def behaviour(self, behaviour: str) -> "_SystemPromptBuilder":
        self._behaviour = behaviour
        return self

    def expectation(self, expectation: str) -> "_SystemPromptBuilder":
        self._expectation = expectation
        return self

    def rule(self, rule: str) -> "_SystemPromptBuilder":
        self._rules.append(rule)
        return self

    def input(self, item: str) -> "_SystemPromptBuilder":
        self._inputs.append(item)
        return self

    def output(self, item: str) -> "_SystemPromptBuilder":
        self._outputs.append(item)
        return self

    def action(self, step: str) -> "_SystemPromptBuilder":
        self._actions.append(step)
        return self

    def reviews(self, reviews: str) -> "_SystemPromptBuilder":
        self._reviews = reviews
        return self

    def build(self) -> SystemPrompt:
        return SystemPrompt(
            name=self._name,
            behaviour=self._behaviour,
            expectation=self._expectation,
            rules=list(self._rules),
            inputs=list(self._inputs),
            outputs=list(self._outputs),
            actions=list(self._actions),
            reviews=self._reviews,
        )


def _section(title: str, body: str) -> str:
    if not body:
        return ""
    return f"{title}:\n{body}"


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item.strip()}" for item in items if item.strip())


def _numbered(items: list[str]) -> str:
    lines = [item.strip() for item in items if item.strip()]
    return "\n".join(f"{index}. {line}" for index, line in enumerate(lines, start=1))

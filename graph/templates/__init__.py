from graph.templates.coder_template import coder_template
from graph.templates.editer_template import editer_template
from graph.templates.proofreader_template import proofreader_template
from graph.templates.summarizer_template import summarizer_template
from graph.templates.intent_analyzer_template import intent_analyzer_template

CODER_TEMPLATE = coder_template()
EDITER_TEMPLATE = editer_template()
SUMMARIZER_TEMPLATE = summarizer_template()
PROOFREADER_TEMPLATE = proofreader_template()
INTENT_ANALYZER_TEMPLATE = intent_analyzer_template()

__all__ = [
    "CODER_TEMPLATE",
    "EDITER_TEMPLATE",
    "SUMMARIZER_TEMPLATE",
    "PROOFREADER_TEMPLATE",
    "INTENT_ANALYZER_TEMPLATE",
]

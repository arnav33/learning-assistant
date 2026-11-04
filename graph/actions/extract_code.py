import re

from bs4 import BeautifulSoup

# `code` is omitted on purpose: it is the one standard tag whose text we keep.
STANDARD_HTML_TAGS = (
    "a", "abbr", "address", "area", "article", "aside", "audio",
    "b", "base", "bdi", "bdo", "blockquote", "body", "br", "button",
    "canvas", "caption", "cite", "col", "colgroup",
    "data", "datalist", "dd", "del", "details", "dfn", "dialog", "div", "dl", "dt",
    "em", "embed",
    "fieldset", "figcaption", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html",
    "i", "iframe", "img", "input", "ins",
    "kbd",
    "label", "legend", "li", "link",
    "main", "map", "mark", "menu", "meta", "meter",
    "nav", "noscript",
    "object", "ol", "optgroup", "option", "output",
    "p", "picture", "pre", "progress",
    "q",
    "rp", "rt", "ruby",
    "s", "samp", "script", "search", "section", "select", "slot", "small", "source", "span",
    "strong", "style", "sub", "summary", "sup",
    "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track",
    "u", "ul",
    "var", "video",
    "wbr",
)
_CODE_TAG = re.compile(rf"^(?!({'|'.join(STANDARD_HTML_TAGS)})$).+")


def extract_code(text: str):
    soup = BeautifulSoup(text, "html.parser")
    code_blocks = []
    for tag in soup.find_all(_CODE_TAG):
        if tag.find(_CODE_TAG):
            continue
        text = tag.get_text().strip()
        if text:
            text = text.strip()
            code_blocks.append(text)
    return code_blocks
import requests
import re
from bs4 import BeautifulSoup



def browse_action(results: list[dict]):
    urls = [
        result.get("href", "").strip()
        for result in results
        if result.get("href", "").strip().startswith(("http://", "https://"))
    ]
    print(f"Urls::{urls}")
    responses = []
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            responses.append({
                "text": _html_to_text(soup),
                "html": response.text,
            })
        else:
            responses.append({
                "text": f"Failed to fetch content from {url}\n\n",
                "html": "",
            })
    return responses

def browse_actions(results: list[dict]) -> list[dict]:
    urls = [
        result.get("href", "").strip()
        for result in results
        if result.get("href", "").strip().startswith(("http://", "https://"))
    ]
    print(f"Urls::{urls}")
    response_text = []
    response_code = []
    for url in urls:
        text = ""
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            response_text.append(_html_to_text(soup))
            response_code.append(extract_code(soup))
        else:
            response_code.append(f"Failed to fetch content from {url}\n\n")
    return response_text, response_code


##########################################################################
############## This section is used to convert HTML to text ##############
##########################################################################
def _html_to_text(soup: BeautifulSoup):

    # Step 2: Elements to completely remove by tag name
    # This gets rid of footers, navigation headers, sidebars, scripts, and styles
    unwanted_tags = [
        "footer",
        "nav",
        "aside",
        "header",
        "script",
        "style",
        "noscript",
        "iframe",
    ]
    for tag in soup(unwanted_tags):
        tag.decompose()

    # Step 3: Elements to remove by common class or id naming patterns
    # Targets structural wrappers commonly named "footer", "sidebar", or "nav"
    unwanted_selectors = [
        "[class*='footer']",
        "[id*='footer']",
        "[class*='sidebar']",
        "[id*='sidebar']",
        "[class*='navigation']",
        "[id*='navigation']",
        "[class*='menu']",
        "[id*='menu']",
    ]
    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()

    # Step 4: Extract the clean main-body text
    text = soup.get_text()

    # Step 5: Filter for standard QWERTY ASCII (32-126) and Newlines (ASCII 10)
    text = "".join(c for c in text if 32 <= ord(c) <= 126 or ord(c) == 10)

    # Step 6: Collapse sequential spaces
    text = re.sub(r" +", " ", text)

    # Step 7: Collapse sequential newlines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()

##########################################################################
## This section is used to determine if a block of text looks like code ##
##########################################################################

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


def extract_code(soup: BeautifulSoup):
    code_blocks = []
    for tag in soup.find_all(_CODE_TAG):
        if tag.find(_CODE_TAG):
            continue
        text = tag.get_text().strip()
        if text:
            code_blocks.append(text)
    return code_blocks

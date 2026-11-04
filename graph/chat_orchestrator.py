from langchain.messages import HumanMessage
from ollama import ResponseError
from langgraph.graph import END, START, StateGraph
from sentence_transformers import SentenceTransformer

from graph.chat_state import ChatState
from graph.nodes.agents import intent_analyzer_agent, proofreader_agent, editer_agent, scorer_agent, summarizer_agent, coder_agent
from graph.nodes.actions import browse_action, filter_action, reference_action, rerank_action, search_action
from graph.nodes.actions.extract_code import extract_code
from graph.templates import CODER_TEMPLATE, EDITER_TEMPLATE, INTENT_ANALYZER_TEMPLATE, SCORER_TEMPLATE, SUMMARIZER_TEMPLATE, PROOFREADER_TEMPLATE
from graph.common import IntentType, invoke, stream

from aop import log_execution, print_timers

_graph = None
_embedder = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


@log_execution
def check_intents(state: ChatState,) -> dict:
    return [intent.value for intent in state["intents"]]


@log_execution
def route_after_best_text(state: ChatState) -> list[str]:
    return [
        intent.value
        for intent in state["intents"]
        if intent.value in (IntentType.COMPACT.value, IntentType.DETAILED.value)
    ]


@log_execution
def proofread_query(state: ChatState) -> dict:
    query = state["query"]
    message = PROOFREADER_TEMPLATE.format(query=query)
    query = stream(proofreader_agent, message)
    print(f"PROOFREADER_QUERY::{query}")
    return {"query": query}


@log_execution
def intent_analysis(state: ChatState) -> dict:
    query = state["query"]
    intent_types = [intent.value for intent in IntentType]
    message = INTENT_ANALYZER_TEMPLATE.format(
        query=query,
        IntentType=intent_types,
    )
    response = intent_analyzer_agent.invoke({
        "messages": [HumanMessage(content=message)],
    })
    intents = response["structured_response"].intent_types
    print(f"INTENTS::{intents}")
    return {"intents": intents}


@log_execution
def search(state: ChatState) -> dict:
    query = state["query"]
    search_results = search_action(query)
    return {"search_results": search_results}


@log_execution
def rerank(state: ChatState) -> dict:
    query, search_results = state["query"], state["search_results"]
    search_results = rerank_action(query, search_results)
    return {"search_results": search_results}


@log_execution
def filter(state: ChatState) -> dict:
    search_results = state["search_results"]
    search_results = filter_action(search_results)
    return {"search_results": search_results}


@log_execution
def browse(state: ChatState) -> dict:
    search_results = state["search_results"]
    browse_responses = browse_action(search_results)
    return {"browse_responses": browse_responses,}


@log_execution
def best_text_finder(state: ChatState) -> dict:
    try:
        query, browse_responses = state["query"], state["browse_responses"]
        chunks = []
        for response in browse_responses:
            text = response["text"]
            chunks.extend([text[i - 500:i + 1500] for i in range(500, len(text), 1000)] or [text])

        embedder = _get_embedder()
        query_embedding = embedder.encode([query], normalize_embeddings=True)
        chunk_embeddings = embedder.encode(chunks, normalize_embeddings=True)
        scores = (chunk_embeddings @ query_embedding.T).ravel()
        best_index = int(scores.argmax())
    except Exception as e:
        print(f"RESPONSE_ERROR::{e}")
        return {"best_text": None}
    best_text = chunks[best_index]
    print(f"BEST_TEXT::{best_text}")
    print(f"BEST_TEXT_LENGTH::{len(best_text)}")
    print(f"BEST_SCORE::{float(scores[best_index])}")
    return {"best_text": best_text}


@log_execution
def best_codes_finder(state: ChatState) -> dict:
    query, browse_responses = state["query"], state["browse_responses"]
    best_code_browse_responses_index = None
    best_code_score = None
    code_objects = []
    for i, response in enumerate(browse_responses):
        extracted_codes = extract_code(response["html"])
        for code in extracted_codes:
            message = SCORER_TEMPLATE.format(query=query, text=code)
            print(f"SCORER_MESSAGE_LENGTH::{len(message)}")
            result = invoke(scorer_agent, message)
            score = result.score
            print(f"SCORER_SCORE::{score}")
            code_obj = {
                "code": code,
                "score": score,
                "response_index": i,
            }
            print(f"CODE_OBJECT::{code_obj}")
            code_objects.append(code_obj)
            if best_code_score is None or score > best_code_score:
                best_code_browse_responses_index = i
                best_code_score = score
    code_objects = [obj for obj in code_objects if obj["response_index"] == best_code_browse_responses_index]
    code_objects = [obj for obj in code_objects if obj["score"] > 0.6]
    codes = [obj["code"] for obj in code_objects]
    codes_char_count = [len(code) for code in codes]
    print(f"CODES_CHAR_COUNT::{codes_char_count}")
    return {"best_codes": codes}

    
# def extract_codes(state: ChatState) -> dict:
#     browse_text = state["browse_text"]
#     raw_codes = extract_code(browse_text)
#     return {"raw_codes": raw_codes}


@log_execution
def reference(state: ChatState) -> dict:
    search_results = state["search_results"]
    references = reference_action(search_results)
    return {"references": references}


@log_execution
def code(state: ChatState) -> dict:
    query, best_codes = state["query"], state["best_codes"]
    message = CODER_TEMPLATE.format(browse_text=best_codes, query=query)
    codes = stream(coder_agent, message)
    return {"codes": codes}


@log_execution
def edit(state: ChatState) -> dict:
    query, best_text = state["query"], state["best_text"]
    message = EDITER_TEMPLATE.format(query=query, data=best_text)
    detailed = stream(editer_agent, message)
    return {"detailed": detailed}


@log_execution
def summarize(state: ChatState) -> dict:
    query, best_text = state["query"], state["best_text"]
    message = SUMMARIZER_TEMPLATE.format(query=query, data=best_text)
    compact = stream(summarizer_agent, message)
    return {"compact": compact}


@log_execution
def _orchestrator():
    graph = StateGraph(ChatState)

    graph.add_node("reference", reference)
    graph.add_node("best_codes_finder", best_codes_finder)
    graph.add_node("best_text_finder", best_text_finder)
    graph.add_node("code", code)
    graph.add_node("edit", edit)
    graph.add_node("summarize", summarize)

    web_chain = proofread_query | intent_analysis | search | rerank | filter | browse
    graph.add_node("web_chain", web_chain)

    graph.add_conditional_edges("web_chain", check_intents, {
        "code": "best_codes_finder",
        "compact": "best_text_finder",
        "detailed": "best_text_finder",
        "reference": "reference",
    })
    graph.add_edge("best_codes_finder", "code")
    graph.add_edge("code", END)
    graph.add_conditional_edges("best_text_finder", route_after_best_text, {
        "compact": "summarize",
        "detailed": "edit",
    })
    graph.add_edge("summarize", END)
    graph.add_edge("edit", END)
    graph.add_edge("reference", END)
    
    if(_graph is None):
        _graph = _graph.compile()
    return _graph


@print_timers
def orchestrate(query: str):
    state: ChatState = {"query": query}
    result = _orchestrator().invoke(state)
    compact = result["compact"] if "compact" in result else None
    detailed = result["detailed"] if "detailed" in result else None
    references = result["references"] if "references" in result else None
    codes = result["codes"] if "codes" in result else None
    return compact, detailed, references, codes


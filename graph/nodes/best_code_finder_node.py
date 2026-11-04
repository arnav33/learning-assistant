from typing import TypedDict

from aop import log_execution
from graph.actions import extract_code
from graph.agents import scorer_agent
from graph.common import invoke
from graph.templates import SCORER_TEMPLATE


class BestCodesFinderState(TypedDict):
    query: str
    browse_responses: list[dict]


@log_execution
def best_codes_finder_node(state: BestCodesFinderState) -> dict:
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

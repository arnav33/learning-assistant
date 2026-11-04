from typing import TypedDict

from aop import log_execution
from sentence_transformers import SentenceTransformer


class BestTextFinderState(TypedDict):
    query: str
    browse_responses: list[dict]


_embedder = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


@log_execution
def best_text_finder_node(state: BestTextFinderState) -> dict:
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

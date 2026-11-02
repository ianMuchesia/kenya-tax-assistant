"""Milestone 2, step 2: search by meaning. The question becomes a vector; the closest chunk vectors win.

    python vector_search.py overlap "Company imenipatia nyumba na gari. Hizo benefits pia zinatozwa tax?"
"""

import json
import math
import sys
from pathlib import Path

from bm25 import load_chunks
from embed import embed


HERE = Path(__file__).resolve().parent


def cosine(a: list[float], b: list[float]) -> float:
    """How similar two vectors are: 1 = same direction (same meaning), 0 = unrelated."""
    dot = 0.0
    length_a = 0.0
    length_b = 0.0
    for position in range(len(a)):
        dot = dot + a[position] * b[position]
        length_a = length_a + a[position] * a[position]
        length_b = length_b + b[position] * b[position]
    return dot / (math.sqrt(length_a) * math.sqrt(length_b))




def load_vectors(method: str) -> dict[str, list[float]]:
    """vectors_overlap.jsonl -> {'overlap-0000': [0.017, -0.005, ...], ...}"""
    vectors = {}
    with (HERE / f"vectors_{method}.jsonl").open(encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            vectors[record["id"]] = record["vector"]
    return vectors



def get_score(result: tuple[float, dict]) -> float:
    return result[0]




class VectorSearch:
    def __init__(self, chunks: list[dict], vectors: dict[str, list[float]]):
        self.chunks = chunks
        self.vectors = vectors

    def search(self, question: str, k: int = 5) -> list[tuple[float, dict]]:
        question_vector = embed(["search_query: " + question])[0]

        results = []
        for chunk in self.chunks:
            similarity = cosine(question_vector, self.vectors[chunk["id"]])
            results.append((similarity, chunk))

        results.sort(key=get_score, reverse=True)
        return results[:k]
    
    
    
if __name__ == "__main__":
    method = sys.argv[1]
    question = sys.argv[2]
    search_engine = VectorSearch(load_chunks(method), load_vectors(method))
    for similarity, chunk in search_engine.search(question):
        print(f"{similarity:5.3f}  {chunk['document']:34} pages {chunk['pages']}  section {chunk['section'][:20]!r:24}")

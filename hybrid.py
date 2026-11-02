"""Milestone 2, step 3: hybrid search. Ask keyword search AND vector search, then merge their two lists.

    python hybrid.py overlap "Turnover tax ni 1% ama 1.5%?"

Merging uses reciprocal rank fusion (RRF): a chunk earns 1 / (RRF_K + rank) from each list it appears in.
Only the RANK counts, not the score, because BM25 scores (like 13.2) and cosine scores (like 0.61) can't be compared.
"""
import sys

from bm25 import BM25, load_chunks
from vector_search import VectorSearch, load_vectors

CANDIDATES = 20   # how many results we take from each search before merging
RRF_K = 60        # the usual value: it stops rank 1 from winning by too much


def get_score(result: tuple[float, dict]) -> float:
    return result[0]





class HybridSearch:
    def __init__(self, keyword_engine, vector_engine):
        self.keyword_engine = keyword_engine
        self.vector_engine = vector_engine

    def search(self, question: str, k: int = 5) -> list[tuple[float, dict]]:
        keyword_results = self.keyword_engine.search(question, CANDIDATES)
        vector_results = self.vector_engine.search(question, CANDIDATES)

        fused_scores = {}     # chunk id -> points so far
        chunk_by_id = {}      # chunk id -> the chunk itself

        for result_list in [keyword_results, vector_results]:

            rank = 1
            for score, chunk in result_list:
                points = 1 / (RRF_K + rank)
                # print(rank, round(points, 4), chunk["document"][:20], chunk["pages"])

                chunk_id = chunk["id"]
                if chunk_id in fused_scores:
                    fused_scores[chunk_id] = fused_scores[chunk_id] + points
                else:
                    fused_scores[chunk_id] = points
                chunk_by_id[chunk_id] = chunk
                rank = rank + 1

        results = []
        for chunk_id in fused_scores:
            results.append((fused_scores[chunk_id], chunk_by_id[chunk_id]))

        results.sort(key=get_score, reverse=True)
        return results[:k]
    
    
    
    
if __name__ == "__main__":
    method = sys.argv[1]
    question = sys.argv[2]
    chunks = load_chunks(method)
    search_engine = HybridSearch(BM25(chunks), VectorSearch(chunks, load_vectors(method)))
    for fused_score, chunk in search_engine.search(question):
        print(f"{fused_score:6.4f}  {chunk['document']:34} pages {chunk['pages']}  section {chunk['section'][:20]!r:24}")

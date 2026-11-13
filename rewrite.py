"""Milestone 4, step 5: query rewriting. People say "PAYE bands"; the Act says "individual rates of tax".

    python rewrite.py "PAYE band ni nini na zote ziko wapi?"

Gemini rewrites the (already masked) question in the words Kenyan tax law uses. We search with BOTH the original and
the rewrite, then merge the two lists the same way hybrid.py does: by rank, with reciprocal rank fusion.
"""
import sys

from bm25 import BM25, load_chunks
from gemini import Gemini
from hybrid import HybridSearch
from vector_search import VectorSearch, load_vectors

CANDIDATES = 20
RRF_K = 60

REWRITE_PROMPT = """Rewrite the user's question as one short question in formal English, using the words that Kenyan tax law
and KRA guides use (for example "individual rates of tax" instead of "PAYE bands", "employment income" instead of
"salary"). Keep every section number, year and amount exactly as written.
Do NOT add anything that is not in the question: no section numbers, no years, no names of Acts, no facts.
Reply with the rewritten question only."""


def get_score(result: tuple[float, dict]) -> float:
    return result[0]


class RewriteSearch:
    def __init__(self, inner_engine, gemini: Gemini):
        self.inner_engine = inner_engine
        self.gemini = gemini

    def rewrite(self, question: str) -> str:
        rewritten = self.gemini.ask(REWRITE_PROMPT, question)
        return rewritten.strip()

    def search(self, question: str, k: int = 5) -> list[tuple[float, dict]]:
        original_results = self.inner_engine.search(question, CANDIDATES)
        rewritten_results = self.inner_engine.search(self.rewrite(question), CANDIDATES)

        fused_scores = {}     # chunk id -> points so far
        chunk_by_id = {}      # chunk id -> the chunk itself

        for result_list in [original_results, rewritten_results]:
            rank = 1
            for score, chunk in result_list:
                points = 1 / (RRF_K + rank)
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
    question = sys.argv[1]
    chunks = load_chunks("overlap")
    hybrid = HybridSearch(BM25(chunks), VectorSearch(chunks, load_vectors("overlap")))
    search_engine = RewriteSearch(hybrid, Gemini())
    print("rewritten:", search_engine.rewrite(question), "\n")
    for fused_score, chunk in search_engine.search(question):
        print(f"{fused_score:6.4f}  {chunk['document']:34} pages {chunk['pages']}  section {chunk['section'][:24]!r:28}")

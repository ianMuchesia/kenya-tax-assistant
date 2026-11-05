"""Milestone 3, step 1: if the question names a section, go straight to it. No model needed.

    python section_lookup.py overlap "What does section 3 of the Income Tax Act say?"

Search can't find "section 3": "3" and "section" are common words, and a number has no meaning for embeddings.
But every chunk already carries its section label, so we look it up, then fill the other places with normal search.
"""


import re
import sys

from bm25 import BM25, load_chunks
from hybrid import HybridSearch
from vector_search import VectorSearch, load_vectors


SECTION_IN_QUESTION = re.compile(r"\bsection\s+(\d+[A-Za-z]*)", re.IGNORECASE)   # "section 12E" -> "12E"
MAIN_ACT = "income-tax-act-2026.pdf"     # "section 3" with no Act named means this one
LOOKUP_SCORE = 99.0                      # looked-up chunks are not scored, so they just get a high number
MAX_PIECES = 2                           # a long section has many pieces: its first 2 are enough


def sections_named_in(question: str) -> list[str]:
    """'What does section 12e say?' -> ['12E']"""
    numbers = []
    for number in SECTION_IN_QUESTION.findall(question):
        numbers.append(number.upper())
    return numbers


def pieces_of_section(chunks: list[dict], number: str) -> list[dict]:
    """The first pieces of this section in the main Act."""
    pieces = []
    for chunk in chunks:
        if chunk["document"] != MAIN_ACT:
            continue
        if chunk["section"].upper() != number:
            continue
        if chunk["is_toc"]:
            continue
        pieces.append(chunk)
        if len(pieces) == MAX_PIECES:
            break
    return pieces



class SectionSearch:
    def __init__(self, inner_engine, chunks: list[dict]):
        self.inner_engine = inner_engine
        self.chunks = chunks

    def search(self, question: str, k: int = 5) -> list[tuple[float, dict]]:
        results = []
        used_ids = []

        # 1. The sections the question names go first.
        for number in sections_named_in(question):
            for chunk in pieces_of_section(self.chunks, number):
                results.append((LOOKUP_SCORE, chunk))
                used_ids.append(chunk["id"])

        # 2. Normal search fills the remaining places, skipping chunks we already have.
        for score, chunk in self.inner_engine.search(question, k + len(results)):
            if chunk["id"] not in used_ids:
                results.append((score, chunk))

        return results[:k]
    
    
    
if __name__ == "__main__":
    method = sys.argv[1]
    question = sys.argv[2]
    chunks = load_chunks(method)
    hybrid = HybridSearch(BM25(chunks), VectorSearch(chunks, load_vectors(method)))
    search_engine = SectionSearch(hybrid, chunks)
    for score, chunk in search_engine.search(question):
        print(f"{score:7.4f}  {chunk['document']:34} pages {chunk['pages']}  section {chunk['section'][:20]!r:24}")

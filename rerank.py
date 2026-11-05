"""Milestone 3, step 2: reranking. Hybrid search finds 20 candidates; a cross-encoder reads each one WITH the question.

    python rerank.py overlap "Turnover tax ni 1% ama 1.5%?"

A cross-encoder is slower but smarter: it looks at the question and the chunk together, so it can only re-order a
short list, not search all 761 chunks.
"""

import sys

from sentence_transformers import CrossEncoder

from bm25 import BM25, load_chunks
from hybrid import HybridSearch
from vector_search import VectorSearch, load_vectors



MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
CANDIDATES = 20   # how many hybrid results the reranker re-orders


def get_score(result: tuple[float,dict])->float:
    return result[0]


class RerankSearch:
    def __init__(self,first_engine):
        self.first_engine = first_engine
        self.model = CrossEncoder(MODEL)
        
    def search(self,question:str,k:int=5)->list[tuple[float,dict]]:
        candidates = self.first_engine.search(question,CANDIDATES)
        
        pairs = []
        
        for score, chunk in candidates:
            pairs.append((question,chunk['text']))
            
            
        new_scores = self.model.predict(pairs)
        
        
        results = []
        
        for position in range(len(candidates)):
            chunk = candidates[position][1]
            results.append((float(new_scores[position]),chunk))
            
            
        results.sort(key=get_score,reverse=True)
        
        return results[:k]
    
    
    
if __name__ == "__main__":
    method = sys.argv[1]
    question = sys.argv[2]
    chunks = load_chunks(method)
    hybrid = HybridSearch(BM25(chunks), VectorSearch(chunks, load_vectors(method)))
    search_engine = RerankSearch(hybrid)
    for new_score, chunk in search_engine.search(question):
        print(f"{new_score:7.3f}  {chunk['document']:34} pages {chunk['pages']}  section {chunk['section'][:20]!r:24}")
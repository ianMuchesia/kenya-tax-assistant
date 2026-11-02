"""Keyword search with BM25, written by hand so every step of the scoring is visible.

    python bm25.py overlap "Turnover tax ni 1% ama 1.5%?"     # top 5 chunks for one question
"""

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
K1 = 1.5    # how fast extra repeats of a word stop helping (the 10th "tax" adds little)
B = 0.75    # how much long chunks are pushed down (0 = not at all, 1 = fully)


def tokenize(text: str) -> list[str]:
    """'Section 12C: Turnover tax!' -> ['section', '12c', 'turnover', 'tax']"""
    lower_text = text.lower()
    words = re.findall(r"[a-z0-9]+", lower_text)
    return words


def count_words(words: list[str]) -> dict[str, int]:
    """['tax', 'rate', 'tax'] -> {'tax': 2, 'rate': 1}"""
    counts = {}
    for word in words:
        if word in counts:
            counts[word] = counts[word] + 1
        else:
            counts[word] = 1
    return counts


class BM25:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        
        # 1. For every chunk: how many times each word appears in it, and how long it is.
        self.word_counts = []     # one dict per chunk, e.g. {'rental': 4, 'tax': 7, ...}
        self.lengths = []         # one number per chunk: how many words it has
        for chunk in chunks:
            words = tokenize(chunk["text"])
            self.word_counts.append(count_words(words))
            self.lengths.append(len(words))
            
            
        total_length = 0
        for length in self.lengths:
            total_length = total_length + length
        self.average_length = total_length / len(self.lengths)
        
        
        
        # 2. For every word: in how many chunks does it appear?
        chunks_containing = {}    # e.g. {'the': 750, 'turnover': 31, ...}
        for counts in self.word_counts:
            for word in counts:
                if word in chunks_containing:
                    chunks_containing[word] = chunks_containing[word] + 1
                else:
                    chunks_containing[word] = 1
                    
                    
                    
        # 3. Rarity of every word (IDF): rare words get a big weight, common words a small one.
        number_of_chunks = len(chunks)
        self.rarity = {}
        for word in chunks_containing:
            appears_in = chunks_containing[word]
            self.rarity[word] = math.log(1 + (number_of_chunks - appears_in + 0.5) / (appears_in + 0.5))
            
            
    def score(self, question_words: list[str], chunk_number: int) -> float:
        """How well one chunk matches the question: add up a score for every question word it contains."""
        counts = self.word_counts[chunk_number]
        chunk_length = self.lengths[chunk_number]
        total = 0.0

        for word in question_words:
            if word not in counts:
                continue                       # this chunk doesn't have the word: adds nothing

            times_in_chunk = counts[word]
            rarity = self.rarity[word]

            # Repeats help, but less and less (the 2nd "tax" counts, the 20th barely does).
            # Long chunks are pushed down a little, so they don't win just by having more words.
            length_ratio = chunk_length / self.average_length
            length_penalty = K1 * (1 - B + B * length_ratio)
            repeat_part = times_in_chunk * (K1 + 1) / (times_in_chunk + length_penalty)

            total = total + rarity * repeat_part

        return total
    
    
    
    def search(self, question: str, k: int = 5) -> list[tuple[float, dict]]:
        """Score every chunk for this question and return the best k, highest score first."""
        question_words = tokenize(question)

        results = []
        for chunk_number in range(len(self.chunks)):
            chunk_score = self.score(question_words, chunk_number)
            results.append((chunk_score, self.chunks[chunk_number]))

        results.sort(key=get_score, reverse=True)
        return results[:k]
    
    
    




def get_score(result: tuple[float, dict]) -> float:
    """Used to sort results: a result is (score, chunk), so the score is item 0."""
    return result[0]


def load_chunks(method: str) -> list[dict]:
    chunks = []
    path = HERE / f"chunks_{method}.jsonl"
    with path.open(encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


if __name__ == "__main__":
    method = sys.argv[1]
    question = sys.argv[2]
    search_engine = BM25(load_chunks(method))
    for chunk_score, chunk in search_engine.search(question):
        print(f"{chunk_score:6.2f}  {chunk['document']:34} pages {chunk['pages']}  section {chunk['section'][:20]!r:24}")


            
            
            
        
        



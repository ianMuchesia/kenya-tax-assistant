"""Milestone 1, step 3: the baseline. For every answerable question: is a right chunk in the top 5?

    python evaluate.py              # all 3 chunking methods, with and without the contents pages

A chunk is "right" if it comes from the answer's document AND covers one of the answer's pages
AND is precise (covers at most MAX_PAGES pages). Without that last rule, a giant chunk covering a whole
booklet "hits" every question about it: the first version of this file was fooled exactly like that.
"""


import csv
from pathlib import Path


from bm25 import BM25, load_chunks
from vector_search import VectorSearch, load_vectors
from hybrid import HybridSearch 
from section_lookup import SectionSearch
from rerank import RerankSearch





HERE = Path(__file__).resolve().parent
TOP_K = 5
MAX_PAGES = 2  # a chunk spanning more pages than this is too vague to count as finding the answer



def load_questions() -> list[dict]:
    """Only the answerable questions: the 10 unanswerable ones are for Milestone 4."""
    questions = []
    with (HERE / "questions.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["answerable"] == "yes":
                questions.append(row)
    return questions




def answer_locations(question: dict) -> list[tuple[str, int]]:
    """Where the answer is, as (document, page) pairs.

    'income-tax-act-2026.pdf' + '62;70'                     -> [('income-tax-act-2026.pdf', 62), ('income-tax-act-2026.pdf', 70)]
    'kra-paye-guide-2022.pdf;income-tax-act-2026.pdf' + '2;109' -> [('kra-paye-guide-2022.pdf', 2), ('income-tax-act-2026.pdf', 109)]
    """
    documents = question["document"].split(";")
    pages = question["page"].split(";")

    locations = []
    for position in range(len(pages)):
        if len(documents) == 1:
            document = documents[0]            # one document, several pages
        else:
            document = documents[position]     # one document per page
        locations.append((document, int(pages[position])))
    return locations





def is_hit(chunk: dict, locations: list[tuple[str, int]]) -> bool:
    """Does this chunk contain the answer, precisely?"""
    if len(chunk["pages"]) > MAX_PAGES:
        return False                            # too big to count: "somewhere in this booklet" is not an answer
    for document, page in locations:
        if chunk["document"] == document and page in chunk["pages"]:
            return True
    return False




def evaluate(search_engine, questions: list[dict]) -> dict:
  

    hits = 0
    total_words = 0
    missed = []
    by_type = {}                                # e.g. {'table': {'hits': 4, 'total': 8}, ...}

    for question in questions:
        results = search_engine.search(question["question"], TOP_K)
        locations = answer_locations(question)
        
        

        found = False
        for chunk_score, chunk in results:
            total_words = total_words + len(chunk["text"].split())   # what the answer model would have to read
            if is_hit(chunk, locations):
                found = True

        question_type = question["type"]
        if question_type not in by_type:
            by_type[question_type] = {"hits": 0, "total": 0}
        by_type[question_type]["total"] = by_type[question_type]["total"] + 1

        if found:
            hits = hits + 1
            by_type[question_type]["hits"] = by_type[question_type]["hits"] + 1
        else:
            missed.append(question["id"])

    return {
        "hits": hits,
        "missed": missed,
        "by_type": by_type,
        "words_per_question": total_words / len(questions),
    }



def without_contents(chunks: list[dict]) -> list[dict]:
    kept = []
    for chunk in chunks:
        if not chunk["is_toc"]:
            kept.append(chunk)
    return kept




def print_result(method: str, label: str, result: dict, number_of_questions: int) -> None:
    percent = result["hits"] / number_of_questions
    line = f"{method:8} {label:14} {result['hits']:2}/{number_of_questions} = {percent:4.0%}   {result['words_per_question']:5.0f} words  "
    for question_type in sorted(result["by_type"]):
        counts = result["by_type"][question_type]
        line = line + f"  {question_type[:9]} {counts['hits']}/{counts['total']}"
    print(line)
    
    
    
    
if __name__ == "__main__":
    questions = load_questions()
    print(f"{len(questions)} answerable questions, top {TOP_K}, overlap chunks\n")
    
    
    
    chunks = load_chunks("overlap")
    vectors = load_vectors("overlap")

    engines = {
        "keyword": BM25(chunks),
        "vector": VectorSearch(chunks, vectors),
    }
    
    engines["hybrid"] = HybridSearch(engines["keyword"], engines["vector"])  
    
    engines["section"] = SectionSearch(engines["hybrid"], chunks)
    
    engines["rerank"] = SectionSearch(RerankSearch(engines["hybrid"]), chunks)





    for name in engines:
        result = evaluate(engines[name], questions)
        print_result(name, "", result, len(questions))
        print(f"{'':24}missed: {' '.join(result['missed'])}")


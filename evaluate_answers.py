"""Milestone 4, step 4: mark Gemini's real answers on all 50 questions, with and without the reranker.

    python evaluate_answers.py        # about 10 minutes the first time; saved answers make reruns fast

What this measures: right refusals, wrong refusals, right citations, made-up citations.
What this does NOT measure: whether the words of the answer are true. For that, read answers_*.txt by hand.
"""


import csv
from pathlib import Path
from rewrite import RewriteSearch

from answer import TaxAssistant
from bm25 import BM25, load_chunks
from evaluate import answer_locations, is_hit
from gemini import Gemini
from hybrid import HybridSearch
# from rerank import RerankSearch
from section_lookup import SectionSearch
from vector_search import VectorSearch, load_vectors



HERE = Path(__file__).resolve().parent


def load_all_questions()-> list[dict]:
    questions = []
    
    with(HERE / "questions.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            questions.append(row)
            
    return questions


def has_right_citation(sources: list[dict], locations: list[tuple[str, int]]) -> bool:
    
    for chunk in sources:
        if is_hit(chunk,locations):
            return True
    return False


def evaluate_answers(name: str, assistant: TaxAssistant, questions: list[dict]) -> None:
    right_citations = 0
    wrong_refusals = []
    wrong_citations = []
    right_refusals = 0
    answered_unanswerable = []
    made_up  = 0
    answerable_total = 0
    unanswerable_total = 0
    
    with (HERE / f"answers_{name}.txt").open("w", encoding="utf-8") as out:
        for question in questions:
            result = assistant.ask(question["question"])
            made_up = made_up + len(result["made_up"])
            
            out.write(f"{question['id']} {question['type']}\nQ: {question['question']}\nA: {result['answer']}\n")
            
            
            for chunk in result["sources"]:
                out.write(f"   source: {chunk['document']}, pages {chunk['pages']}\n")
            out.write("\n")

            if question["answerable"] == "yes":
                answerable_total = answerable_total + 1
                if result["refused"]:
                    wrong_refusals.append(question["id"])
                elif has_right_citation(result["sources"], answer_locations(question)):
                    right_citations = right_citations + 1
                else:
                    wrong_citations.append(question["id"])
            else:
                unanswerable_total = unanswerable_total + 1
                if result["refused"]:
                    right_refusals = right_refusals + 1
                else:
                    answered_unanswerable.append(question["id"])

    print(f"{name}")
    print(f"  right citation       {right_citations}/{answerable_total}")
    print(f"  wrong citation       {len(wrong_citations)}   {' '.join(wrong_citations)}")
    print(f"  wrong refusal        {len(wrong_refusals)}   {' '.join(wrong_refusals)}")
    print(f"  right refusal        {right_refusals}/{unanswerable_total}")
    print(f"  should have refused  {len(answered_unanswerable)}   {' '.join(answered_unanswerable)}")
    print(f"  made-up citations    {made_up}")


if __name__ == "__main__":
    questions = load_all_questions()
    chunks = load_chunks("overlap")
    hybrid = HybridSearch(BM25(chunks), VectorSearch(chunks, load_vectors("overlap")))
    gemini = Gemini()

    assistants = {
        # "with_reranker": TaxAssistant(SectionSearch(RerankSearch(hybrid), chunks), gemini),
        "no_reranker": TaxAssistant(SectionSearch(hybrid, chunks), gemini),
        "no_rewrite": TaxAssistant(SectionSearch(hybrid, chunks), gemini),
        "rewrite": TaxAssistant(SectionSearch(RewriteSearch(hybrid, gemini), chunks), gemini),
    }

    for name in assistants:
        evaluate_answers(name, assistants[name], questions)


    
    
     





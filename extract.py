"""Milestone 1, step 1: get the text out of every PDF in docs/, one record per page.

    python extract.py          # writes pages.jsonl and prints a summary per document

Every page keeps its document, year and page number, so every chunk (and every citation) can point back to it.
"""

import json
import re
import unicodedata
from pathlib import Path


import pymupdf


HERE = Path(__file__).resolve().parent
DOCS = HERE / "docs"
OUT = HERE / "pages.jsonl"



def year_of(filename: str) -> int | None:
    """finance-act-2025.pdf -> 2025. The year is in the file name on purpose (for the year filter later)."""
    match = re.search(r"(20\d\d)", filename)
    return int(match.group(1)) if match else None



def clean(text: str) -> str:
    """NFKC turns printer ligatures into plain letters: 'proﬁt' -> 'profit'. Otherwise keyword search misses them."""
    return unicodedata.normalize("NFKC", text)



def extract_pdf(path:Path) -> list[dict]:
    pages = []
    
    with pymupdf.open(path) as pdf:
        for number, page in enumerate(pdf, start=1):
            pages.append({
                "document": path.name,
                "year": year_of(path.name),
                "page": number,
                "text": clean(page.get_text()),
            })
     
    
    return pages
            
            
            
if __name__ == "__main__":
    total = 0
    with OUT.open("w", encoding="utf-8") as out:
        for path in sorted(DOCS.glob("*.pdf")):
            pages = extract_pdf(path)
            empty = sum(1 for p in pages if not p["text"].strip())
            words = sum(len(p["text"].split()) for p in pages)
            print(f"{path.name:36} {len(pages):4} pages  {words:7} words  {empty} empty pages")
            for p in pages:
                out.write(json.dumps(p, ensure_ascii=False) + "\n")
            total += len(pages)
    print(f"\n{total} pages written to {OUT.name}")

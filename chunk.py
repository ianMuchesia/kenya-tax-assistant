"""Milestone 1, step 2: split pages.jsonl into chunks, 3 different ways, so we can measure which is best.

    python chunk.py        # writes chunks_fixed.jsonl, chunks_heading.jsonl, chunks_overlap.jsonl

A: fixed      every SIZE words, no matter what
B: heading    one chunk per section: "6A. ..." in the Acts, "What is ...?" in the KRA guides
C: overlap    like B, but sections longer than SIZE words are cut into pieces that share OVERLAP words
"""


import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIZE = 300     # words per chunk (about half a page)
OVERLAP = 50   # words repeated between two pieces of the same long section (method C)

ACT_HEADING = re.compile(r"^\s*(\d+[A-Z]*)\.(\s+\S|\s*$)")  # "6A. Imposition..." or "6A." alone on its line
TOC_LINE = re.compile(r"\.{5,}")                             # "6A. Imposition ......."  (contents pages)

def load_documents()->dict[str, list[dict]]:
    docs = defaultdict(list)
    
    for line in (HERE/"pages.jsonl").open(encoding="utf-8"):
        page = json.loads(line)
        docs[page["document"]].append(page)
       
        
        
  
        
    return docs

def words_with_pages(pages: list[dict]) -> list[tuple[str, int]]:
    """Every word of a document, with the page it is on, so a chunk always knows its page(s)."""
    result = []
    for p in pages:                         # each page of the document
        for word in p["text"].split():      # cut the page's text into words
            result.append((word, p["page"]))   # save the word WITH its page number
    return result



def make_chunk(method:str , doc:str, year:int, words:list[tuple[str,int]],section:str ="")->dict:
    unique_pages = set()                  # an empty set
    for _, page in words:
        unique_pages.add(page)            # adding 26 a second time does nothing
    pages = sorted(unique_pages)          # → [26, 27]

    text = " ".join(word for word,_ in words)
    return {
        "method":method,
        "document":doc,
        "year": year,
        "pages": pages,
        "section":section,
        "is_toc": len(TOC_LINE.findall(text)) >= 3, "text": text
    }
    
    
def windows(words: list, size: int, step: int):
    """Cut a list into pieces of `size`, moving `step` each time (step < size = overlap)."""
    for start in range(0, len(words), step):
        yield words[start:start + size]
        if start + size >= len(words):
            break
        
        
        
        



# --- method A: fixed size --------------------------------------------------------------------------

def chunk_fixed(doc: str, pages: list[dict]) -> list[dict]:
    # print(pages[:10])
    words = words_with_pages(pages)
    # print(words)
    year = pages[0]["year"]                    # the document's year (every page has the same year)

    chunks = []                                # an empty basket
    for piece in windows(words, SIZE, SIZE):   # cut the words into pieces of 300
        chunk = make_chunk("fixed", doc, year, piece)   # turn one piece into one chunk record
        chunks.append(chunk)                   # put it in the basket
    return chunks


# --- method B: by heading ---------------------------------------------------------------------------

def is_heading(line: str, is_act: bool) -> str | None:
    """Returns the section name if this line starts a new section, else None."""
    if is_act:
        match = ACT_HEADING.match(line)          # does the line look like "6A." ?

        if match is None:                        # no, it doesn't start with a section number
            return None

        if TOC_LINE.search(line):                # it does, but it has "......." → a contents-page line
            return None

        return match.group(1)                    # a real heading → give back just the number, e.g. "6A"

    line = line.strip()
    if line.endswith("?") and len(line.split()) <= 15:   # KRA guides: "What is the MRI tax rate?"
        return line
    if line.isupper() and 1 <= len(line.split()) <= 8:   # KRA guides: "PAYE AS YOU EARN (PAYE)"
        return line
    return None




def sections(doc: str, pages: list[dict]) -> list[tuple[str, list[tuple[str, int]]]]:
    """Walk the document line by line; start a new section at every heading."""
    is_act = "act" in doc
    found, name, words = [], "(start)", []
    for p in pages:
        for line in p["text"].splitlines():
            heading = is_heading(line, is_act)
            if heading and words:
                found.append((name, words))
                words = []
            if heading:
                name = heading
            for w in line.split():              # cut the line into words
                words.append((w, p["page"]))    # add each word, with its page number, to the current section

    if words:
        found.append((name, words))
    return found



def chunk_heading(doc: str, pages: list[dict]) -> list[dict]:
    year = pages[0]["year"]                    # the document's year

    chunks = []                                # an empty basket
    for name, words in sections(doc, pages):   # the document, already split at every heading
        chunk = make_chunk("heading", doc, year, words, name)   # one section = one chunk
        chunks.append(chunk)
    return chunks



def chunk_overlap(doc: str, pages: list[dict]) -> list[dict]:
    year = pages[0]["year"]
    step = SIZE - OVERLAP                        # 300 - 50 = 250: how far to move each time

    chunks = []
    for name, words in sections(doc, pages):     # 1. cut at headings (same as method B)
        for piece in windows(words, SIZE, step): # 2. cut each section into 300-word pieces, moving 250 each time
            chunk = make_chunk("overlap", doc, year, piece, name)   # every piece keeps its section's name
            chunks.append(chunk)
    return chunks


METHODS = {
    "fixed": chunk_fixed,
    "heading": chunk_heading,
    "overlap": chunk_overlap,
}

if __name__ == "__main__":
    docs = load_documents()
    for method in METHODS:
        fn = METHODS[method]
        chunks = []                                  # 1. an empty basket
        for doc, pages in docs.items():              # 2. for each document folder
           

            for c in fn(doc, pages):                 # 3. chop this document into chunks, then for each chunk
                chunks.append(c) 
                
                # 4. put it in the basket
                 
        # print(chunks)

        for i, c in enumerate(chunks):
            c["id"] = f"{method}-{i:04d}"
        with (HERE / f"chunks_{method}.jsonl").open("w", encoding="utf-8") as out:
            for c in chunks:
                out.write(json.dumps(c, ensure_ascii=False) + "\n")
        sizes = sorted(len(c["text"].split()) for c in chunks)
        print(f"{method:8} {len(chunks):5} chunks   words per chunk: min {sizes[0]:4}  median {sizes[len(sizes) // 2]:4}"
              f"  max {sizes[-1]:5}   contents-page chunks: {sum(c['is_toc'] for c in chunks)}")



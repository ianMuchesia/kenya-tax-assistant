"""Milestone 2, step 1: turn every chunk into a vector (its "meaning address") with nomic-embed-text in Ollama.

    python embed.py overlap        # writes vectors_overlap.jsonl: one {"id", "vector"} per chunk

nomic-embed-text wants a label in front of the text: "search_document: " for chunks, "search_query: " for questions.
"""


import json
import sys
import time
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "nomic-embed-text"
BATCH = 16    # chunks sent to Ollama in one request



def embed(texts: list[str])->list[list[float]]:
    body = {"model": MODEL, "input": texts}
    body_bytes = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(OLLAMA_URL, data=body_bytes, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request) as response:
        answer = json.loads(response.read())
    return answer["embeddings"]


def load_chunks(method: str) -> list[dict]:
    chunks = []
    path = HERE / f"chunks_{method}.jsonl"
    with path.open(encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks




if __name__ == "__main__":
    method = sys.argv[1]
    chunks = load_chunks(method)
    start_time = time.time()

    with (HERE / f"vectors_{method}.jsonl").open("w", encoding="utf-8") as out:
        for start in range(0, len(chunks), BATCH):
            batch = chunks[start:start + BATCH]

            texts = []
            for chunk in batch:
                texts.append("search_document: " + chunk["text"])

            vectors = embed(texts)

            for position in range(len(batch)):
                record = {"id": batch[position]["id"], "vector": vectors[position]}
                out.write(json.dumps(record) + "\n")

            print(f"{start + len(batch)}/{len(chunks)} chunks", end="\r")

    seconds = time.time() - start_time
    print(f"\n{len(chunks)} vectors of {len(vectors[0])} numbers in {seconds:.0f} seconds")

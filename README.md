# Kenya tax assistant

Answers questions about Kenyan tax **from real KRA documents**, with a **citation for every answer**, and
**remembers each user's situation** across sessions.

```
question -> (memory: who is this user?) -> search the documents -> best sections -> Gemini writes the answer
                                                                                 -> cites every section
                                                                                 -> refuses if the sources are weak
```

Project 2 (the M-Pesa refund agent) was about making a workflow safe. This one is about **retrieval**: finding
the right text before the model answers. Every milestone has one main number: **is the right section in the top 5?**

## The milestones

| # | Milestone | The number |
|---|---|---|
| 0 | **Write 50 test questions first**, each with the document + section that answers it | (the questions are the ruler) |
| 1 | Loading and chunking: 3 ways to split, keyword search only | top-5 hit rate per split method (**the baseline**) |
| 2 | Embeddings + hybrid search (reciprocal rank fusion) | keyword vs embeddings vs both, per question type |
| 3 | Reranking + query rewriting + year filter | top-5 again, and how much slower |
| 4 | Answers with citations, refusals when sources are weak | correct refusals (of 10) vs wrong refusals |
| 5 | Memory: conversation, session summaries, long-term facts with corrections | 30-turn test: old fact or new fact at turn 30? |
| 6 | Memory + search together, one token budget | top-5 with memory on vs off |
| 7 | Our own MCP server (raw JSON-RPC first), used from Claude Code | it works from Claude Code |
| 8 | The write-up, from `decisions.md` and the numbers | "from X to Y, and why" |

**Rule:** don't start the next milestone until the current one's number is written below.

## Milestone 0: the question set

The questions are written **by hand, before building anything** (otherwise we'd unknowingly write questions the
system already handles). Mix on purpose:

- different words from the document ("salary" vs "employment income")
- an exact section number or term
- the answer is in a table
- the answer is split across two sections
- a rule that changed between the two Finance Acts
- **10 questions the documents don't answer at all**

## Numbers

| Milestone | Result |
|---|---|
| 1 | |

## Setup

- Python 3.10+, Ollama with `nomic-embed-text` (and `qwen2.5:3b` for small jobs).
- Postgres + pgvector in Docker.
- A Gemini API key in an environment variable (never in git).

(Exact commands are added as each milestone needs them.)

## Progress

- [x] Day 1: decisions made (`decisions.md`), `CLAUDE.md` rules
- [x] Documents chosen and downloaded into `docs/` (6 PDFs; see `decisions.md`)
- [x] Milestone 0: 50 questions written (`questions.csv`); adviser check of the categories still to do
- [ ] Milestone 1: loading and chunking
- [ ] Milestone 2: embeddings and hybrid search
- [ ] Milestone 3: reranking and query rewriting
- [ ] Milestone 4: answers with citations and refusals
- [ ] Milestone 5: memory
- [ ] Milestone 6: memory + search together
- [ ] Milestone 7: MCP server
- [ ] Milestone 8: write-up

**Next step:** Milestone 1, step 1: type `extract.py` (PDF -> `pages.jsonl`, one record per page, NFKC cleaning).

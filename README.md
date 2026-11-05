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
| 1 | Keyword search (BM25), top 5, strict scoring: overlap chunks **28/40 = 70%** (~1,050 words sent; 26/40 before fixing 2 wrong answer keys); fixed 20/40, heading 20/40. Contents pages: no effect. Weakest: exact_section 4/8, table 4/8. 11 questions missed by every method. |
| 2 | Overlap chunks, top 5: keyword 28/40 = 70%; embeddings (nomic-embed-text) 27/40 = 68%; **hybrid (RRF) 31/40 = 78%**, ~930 words sent. Keyword and embeddings miss different questions, so merging them helps. |
| 3 | Overlap chunks, top 5: section lookup + hybrid 33/40 = 82%; **section lookup + hybrid + multilingual reranker 35/40 = 88%**, ~1,070 words sent, about 7 seconds per question on CPU. Reranker alone: 31/40, no gain. Top-1 hits: hybrid 19, section 24, both 21. |

## Setup

- Python 3.10+, Ollama with `nomic-embed-text` (and `qwen2.5:3b` for small jobs).
- Postgres + pgvector in Docker.
- A Gemini API key in an environment variable (never in git).

(Exact commands are added as each milestone needs them.)

## Progress

- [x] Day 1: decisions made (`decisions.md`), `CLAUDE.md` rules
- [x] Documents chosen and downloaded into `docs/` (6 PDFs; see `decisions.md`)
- [x] Milestone 0: 50 questions written (`questions.csv`); adviser check of the categories still to do
- [x] Milestone 1: loading, chunking, keyword search, baseline (65%)
- [x] Milestone 2: embeddings and hybrid search (78%)
- [x] Milestone 3: section lookup and reranking (88%); year filter not built
- [ ] Milestone 4: answers with citations and refusals
- [ ] Milestone 5: memory
- [ ] Milestone 6: memory + search together
- [ ] Milestone 7: MCP server
- [ ] Milestone 8: write-up

**Next step:** Milestone 4: Gemini writes answers with citations and refuses when the documents don't answer (the 10
unanswerable questions). Needs a Gemini API key in `.env`. Does the reranker stay? Decide here, by answer quality. Still
missed: Q004 Q007 Q022 Q038 Q039. Each machine needs `python embed.py overlap` (~9 min, not in git), and the reranker
needs torch, sentence-transformers and a 470 MB model, so run that at work, not at home.

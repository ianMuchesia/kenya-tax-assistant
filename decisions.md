# Decisions

One line (or a few) each time we choose something, and why. This becomes the Milestone 8 write-up.

## 2026-10-30: day 1

- **Database: Postgres + pgvector, in Docker.** One database for chunks, vectors, keyword search and memories, and
  Postgres is what job postings ask for. Docker is already on the work laptop. Rejected: SQLite + sqlite-vec
  (lighter, but less job-relevant). Cost: Docker is also needed on the home Linux machine.
- **Answer model: Gemini Flash (hosted), not a local 7B.** A local 7B on this CPU would be slow. Consequences:
  (1) text sent to Gemini leaves the machine, so KRA PINs / ID numbers are masked first; (2) tokens cost money,
  so tokens are counted per answer from the start; (3) an API key is needed, kept out of git.
- **Embeddings: `nomic-embed-text` in Ollama (local).** Embedding all chunks is many calls; local is free and private.
- **Small jobs (e.g. query rewriting): qwen2.5:3b (local)**, unless measurements say Gemini is needed.
- **Who does what:** M1–M3 retrieval uses no paid model (code, local embeddings, Qwen for rewriting, a local
  reranker). Qwen also extracts memory facts and writes session summaries (M5). **Gemini only writes the final
  answer** (M4/M6): reading the chunks, citing, refusing. Because of Gemini's rate limits: the answer model is
  swappable (develop with Qwen, measure with Gemini), retry with a wait on HTTP 429, cache answers, count calls.
- **PDF extraction: PyMuPDF first**, Docling only if tables come out garbled.
- **PDFs are committed to git** (public documents, small): both machines measure against the exact same files.
  The database is not in git: it is rebuilt from `docs/` on each machine.
- **Plain Python, no RAG framework**, so every step is visible.

## 2026-10-30: the documents (`docs/`)

| File | Source | Why |
|---|---|---|
| `kra-paye-guide-2022.pdf` | KRA | salary questions; **older than the Acts**, so it may state rules that later changed |
| `kra-turnover-tax-guide-2024.pdf` | KRA "Everything About Turnover Tax" | small-business questions |
| `kra-rental-income-guide-2024.pdf` | KRA "Overview of Monthly Rental Income Tax" | landlord questions |
| `income-tax-act-2026.pdf` | KRA copy of Cap. 470 | the law itself: sections and schedules (tables) |
| `tax-laws-amendment-act-2024.pdf` | Kenya Law, Act No. 12 of 2024 | the 2024 changes (**there was no Finance Act 2024**: the bill was withdrawn) |
| `finance-act-2025.pdf` | Kenya Law, Act No. 9 of 2025 | rule changes, year 1 |

- **No Finance Act 2026:** it was not on Kenya Law yet (2026-10-30). The two years of changes are 2024 (Tax Laws
  Amendment Act) and 2025 (Finance Act); the Income Tax Act PDF is the 2026 revision, i.e. the current law.

- File names carry the year, so the Milestone 3 year filter can read it.
- Kenya Law blocks scripted downloads (bot protection), so its Acts were downloaded by hand in a browser.
- **2026-10-31, answer keys checked against the extracted text:** the first draft said the debenture definition
  was changed by the Tax Laws (Amendment) Act 2024; the word "debenture" is not in that Act at all; it was the
  Finance Act 2025, s.2 (p3). An answer key written from memory was wrong. Q036 now tests exactly that trap.
  Score by **section number + document**, not by section title (titles get paraphrased).
- Known traps worth questions: "What did the Finance Act 2024 change?" (there wasn't one); the rental income rate
  differs between older and newer sources; the 2022 PAYE guide vs the newer Acts (two of our own sources disagree).

## 2026-11-02: Milestone 1 baseline

- **Strict scoring:** a chunk counts as a hit only if it is from the right document, covers a right page, and covers
  **at most 2 pages**. The first version had no size rule and the PAYE guide's one giant chunk (pages 2-8) "hit"
  every PAYE question: heading chunking looked best (30/40) only because of that. Measure the measurement.
- **Overlap chunking chosen** (heading sections, long ones cut into 300 words sharing 50): 26/40 = 65%, vs 20/40 for
  fixed and heading, and it sends the fewest words (~1,050 per question).
- **Contents pages kept:** removing them changed nothing.
- Weak spots for Milestone 2: exact_section 4/8, table 4/8; Swahili/Sheng words score 0 (they are in no document);
  no stemming ("tax" is not "taxes"). 11 questions are missed by every chunking method, so chunking is not their problem.
- **Two answer keys fixed after looking at the misses:** Q023 pointed at turnover guide page 4, which is blank (the
  penalty text is on page 3); Q018 now accepts PAYE guide page 2 (table row) or 4 (the explanation). Baseline 26 -> 28/40.

## 2026-11-02: Milestone 2, embeddings and hybrid search

- **Vectors in a plain file** (`vectors_overlap.jsonl`, 761 x 768 numbers, 7.8 MB, not in git), not Postgres yet:
  761 chunks are small and the file shows exactly what a vector is. Building it takes ~9 minutes on the work laptop CPU.
- nomic-embed-text needs the labels `search_document: ` (chunks) and `search_query: ` (questions).
- **Embeddings alone did not beat keywords** (27 vs 28/40), but they miss different questions. Hybrid with reciprocal
  rank fusion (top 20 from each, RRF_K = 60) gives **31/40 = 78%**. RRF uses ranks, not scores, because BM25 and
  cosine scores are on different scales.
- Section-number questions (Q009, Q012) fail with both engines: a number has no "meaning". Fix planned in Milestone 3
  (look up the chunk's section label), not with a better embedding model.

## 2026-11-05: Milestone 3, section lookup and reranking

- **Reranker alone gave no gain:** `mmarco-mMiniLMv2-L12-H384-v1` on the hybrid top 20 scored 31/40 (same as hybrid), and
  the English `ms-marco-MiniLM-L-6-v2` 30/40. Both pushed exact-section answers down (6/8 -> 4/8).
- **Section lookup** (question names a section -> its first 2 pieces in the Income Tax Act go first): 33/40, top-1 hits
  19 -> 24, no model needed. Beat the reranker, so the order of work changed.
- **Together:** 35/40 = 88%, but top-1 falls from 24 to 21, and each question costs about 7 seconds on CPU plus a 470 MB
  model. **Keep or drop the reranker in Milestone 4,** by answer quality. 35 vs 33 is only 2 questions of 40.
- **Be careful with these numbers:** the lookup was written after seeing Q009, Q012 and Q014 fail, so exact_section 8/8
  is flattering. There is no separate test set. It misses "kifungu cha 3", and always assumes the Income Tax Act.
- 16 Act chunks carry the label "3" because schedule paragraphs are numbered too. The lookup works only because real
  sections come first in the file.
- Models were checked by running them on our questions; nothing proved the multilingual model was trained on Swahili.

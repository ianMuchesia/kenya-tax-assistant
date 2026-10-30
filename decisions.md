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
- Known traps worth questions: "What did the Finance Act 2024 change?" (there wasn't one); the rental income rate
  differs between older and newer sources; the 2022 PAYE guide vs the newer Acts (two of our own sources disagree).

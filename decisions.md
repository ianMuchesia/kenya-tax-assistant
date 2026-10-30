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
- **PDF extraction: PyMuPDF first**, Docling only if tables come out garbled.
- **PDFs are committed to git** (public documents, small): both machines measure against the exact same files.
  The database is not in git: it is rebuilt from `docs/` on each machine.
- **Plain Python, no RAG framework**, so every step is visible.

# CLAUDE.md: how we work in this project

This project is a **learning project**. The goal is AI engineering skill (retrieval, evals, memory, MCP),
not just a working app. Read `README.md` (plan + progress) and `decisions.md` (choices made so far) first.

## Rules for Claude

1. **I type all the code myself.** Never write or edit code in my project files. Test ideas in a scratch folder,
   show me the real output, then give me the code in small pieces with a short explanation for each.
   (README.md, decisions.md and this file are documents: you may edit those when I ask.)
2. **Explain every design choice before writing code.** Say what the options are, which one you recommend and why.
   Invite my decision.
3. **No frameworks unless I ask** (no LangChain, LlamaIndex, etc.). Plain Python, so I see every step.
4. **Every feature needs a test or a measurement.** Don't move to the next milestone until its number is written
   down in README.md.
5. **One milestone at a time.** Don't create files ahead of the current milestone.
6. **Simple English.** Short sentences, real output, step-by-step traces, analogies. Long-form code when I ask.
7. **Show commands before running them.** Nothing installed or run "in secret". I run installs myself.
8. **Measure before trusting.** Rerun the full question set after every change; one run can be luck.

## Privacy rules

- Answers are written by **Gemini Flash (hosted)**: everything sent to it leaves my machine.
- **KRA PINs, ID numbers and phone numbers are masked before** anything is sent to Gemini or saved to memory.
- The API key lives in an environment variable / `.env` file, **never in git**.

## Two machines

I alternate between **work (Windows, cmd)** and **home (Linux, slow internet)**. GitHub is the link.

- Start of a session: `git pull`, then check the README "Progress" section.
- End of a session: commit + push, and update the README "Next step" line.
- Commands: work `.venv\Scripts\python ...`, home `.venv/bin/python ...`.
- No big downloads at home (models, Docker images, wheels): do them at work, copy them home.
- The database is **rebuilt from `docs/` on each machine** (it is not in git); the PDFs are in git.

## Where we are

See the "Progress" section in README.md.

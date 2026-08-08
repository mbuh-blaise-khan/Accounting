# Project Progress Log — Universal Accounting Learning & Practice Platform

HOW TO USE THIS FILE:
- This file is the project's memory. It is tool-agnostic — it works whether
  you're using Cline, Copilot, ChatGPT, Gemini, or a fresh Claude chat.
- At the end of every build session, the AI you're working with should add a
  new entry below (newest at the top) summarizing what happened.
- If you ever start a new chat/tool because of a rate limit or a switch, your
  FIRST message should be: "Read the attached PROGRESS_LOG.md and
  .clinerules (or paste their contents) — this is where we left off. We are
  about to start Session X." Then paste this file's contents plus the
  relevant Session X prompt from the build guide.
- Do not delete old entries. This is a running history, not just a status.

---

## Current Status

**Last completed session:** Session 0 — Product Definition & Repo
**Next session to run:** Session 1 — Local Development Environment
**Blockers / open questions:** (none)

---

## Session Log

### Session 0 — Product Definition & Repo
- Status: DONE
- Date completed: 2026-08-08
- What was built:
  - Git repo confirmed (branch `main`); initial commit created.
  - Full folder structure per .clinerules repository layout (created with
    `.gitkeep` files in empty dirs).
  - `docs/blueprint-summary.md` — vision, three modes, accounting chain, MVP
    definition, guardrails.
  - `docs/acceptance-criteria.md` — testable checklist for Sessions 1–11 plus
    cross-cutting MVP requirements.
  - Root `.gitignore` for Python + Node monorepo.
  - Root `.env.example` with DATABASE_URL, SECRET_KEY, JWT, ENV, FRONTEND_ORIGIN.
  - Root `README.md` (placeholder onboarding; Getting Started added in Session 1).
- Decisions made:
  - No application code written in Session 0 (per the guide) — scaffolding/docs
    only.
  - Acceptance criteria will be compared against the build at end of Session 11.
- What Session 1 needs to know:
  - Set up the backend Python venv + requirements.txt, backend/.env.example,
    the Vite+React+Tailwind frontend, and put exact/verified commands in
    README.md "Getting Started" + troubleshooting.

### Session 1 — Local Development Environment
- Status: NOT STARTED

### Session 2 — Project Skeleton
- Status: NOT STARTED

### Session 3 — Authentication + Language Preference
- Status: NOT STARTED

### Session 4 — Workspace & Framework Selection
- Status: NOT STARTED

### Session 5 — Chart of Accounts
- Status: NOT STARTED

### Session 6 — First Transaction
- Status: NOT STARTED

### Session 7 — Cash Book and Journal
- Status: NOT STARTED

### Session 8 — General Ledger
- Status: NOT STARTED

### Session 9 — Trial Balance
- Status: NOT STARTED

### Session 10 — Financial Statements
- Status: NOT STARTED

### Session 11 — Learning Engine (basic) — MVP complete
- Status: NOT STARTED

---

## Key decisions that must never be re-litigated by a new AI/tool

(These get filled in as you go — examples of the kind of thing to lock in
here once decided, so a new tool doesn't quietly redo it differently:)

- Framework field values used in the database (e.g. exact string "OHADA" vs
  "ohada" vs enum name) — (decide in Session 4)
- Exact currency/decimal precision chosen — (default XAF, zero decimals,
  configurable per org; Session 4)
- JWT strategy used (library, token lifetime) — (python-jose, HS256, 60 min in
  .env.example; Session 3)
- Illustrative chart-of-accounts account codes chosen in Session 5 — (decide in
  Session 5)
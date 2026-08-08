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

**Last completed session:** Session 1 — Local Development Environment (partially built)
**Next session to run:** Session 2 — Project Skeleton
**Blockers / open questions:**
- `pip install -r backend/requirements.txt` and `frontend/npm install` could NOT
  be executed by the agent — the build environment has no working network route
  to PyPI/npm (installs hang, no packages download). This is unrelated to the
  project files (shell + venv work fine). The USER must run these installs
  locally per README "Getting Started" and confirm.
- PostgreSQL is NOT installed on this machine (psql/pg_ctl/createdb absent). The
  USER must install PG and run the create-user/database commands from README.
- No code app written yet — `backend/app/main.py` and the api service come in
  Session 2. Session 2 cannot run/verify against the DB until PG + installs are
  done.

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
- Status: PARTIALLY BUILT — scaffolding/config complete; installs + DB pending
  user action
- Date completed: 2026-08-08
- What was built:
  - Backend venv created at `backend/.venv` (Python 3.12.8 confirmed working).
  - `backend/requirements.txt` (fastapi, uvicorn[standard], sqlalchemy, alembic,
    psycopg2-binary, python-dotenv, pydantic, pydantic-settings,
    passlib[bcrypt], python-jose[cryptography], python-multipart, pytest, httpx).
  - `backend/.env.example` (DATABASE_URL, SECRET_KEY, ENV, FRONTEND_ORIGIN).
  - Frontend scaffolded manually (Vite + React + Tailwind v4): `package.json`,
    `vite.config.js`, `index.html`, `src/main.jsx`, `src/App.jsx`,
    `src/index.css`. Uses Tailwind v4 via the `@tailwindcss/vite` plugin (no
    postcss/tailwind.config needed).
  - README.md rewritten with full "Getting Started" (exact commands for venv,
    deps, Postgres install + create user/db, running backend + frontend) plus a
    Windows/Mac/Linux troubleshooting section for Postgres errors.
  - Fixed a stray-quote typo in docs/blueprint-summary.md MVP-definition line.
  - Added scripts/.gitkeep (scripts/ dir was empty).
- Decisions made:
  - SQLAlchemy 2.0 (declarative) chosen (requirements.txt). Alembic for
    migrations.
  - JWT: passlib[bcrypt] + python-jose[cryptography]; SECRET_KEY/60-min defaults
    recorded in .env.example (finalized in Session 3).
  - Tailwind v4 + @tailwindcss/vite plugin (no tailwind.config.js).
  - Default local DB/user: `uap_dev` / `uap`, password `uap_dev_password`,
    DATABASE_URL port 5432.
- What Session 2 needs to know:
  - Session 2 builds backend/app/main.py (CORS for http://localhost:5173),
    database connection from backend/.env DATABASE_URL, Alembic initial empty
    migration, GET /health with real DB ping, frontend api service calling
    /health, + one pytest.
  - Before Session 2 can be verified, user must run: venv activation + pip
    install, PostgreSQL install + create user/db, and npm install (all commands
    in README).
  - The `scripts/` folder may be used to store helper scripts (seeds, run
    helpers) later.

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
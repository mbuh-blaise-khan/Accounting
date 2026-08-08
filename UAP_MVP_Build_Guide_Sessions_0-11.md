# Universal Accounting Platform — MVP Build Guide (Sessions 0–11)

This is your working companion to the blueprint. It turns Sessions 0–11 (the exact
scope the blueprint calls the MVP path — "Stop after Session 10 or 11 and have a
usable local application") into prompts you paste into **Cline, inside VS Code**,
one session at a time. Each prompt assumes the previous one's work already exists on
disk — don't skip ahead.

**Scope reminder from the blueprint:** Version 1 is a **responsive web app**
(React + Tailwind + FastAPI + PostgreSQL), not a native mobile app. Mobile-native is
explicitly a later phase, and the web app must be usable on a phone browser from day
one. AI, payments, and advanced analytics come after this guide, not during it.

---

## 0. How this workflow actually works

1. Open VS Code on your project folder (the one with `.git`, `.clinerules`,
   and `PROGRESS_LOG.md` already in it).
2. Open Cline from the VS Code sidebar. Make sure your free API key
   (e.g. Google Gemini) is set in Cline's settings.
3. For each session below: paste the prompt into Cline's chat box, let it
   plan and write the code, **run the app and actually click through what
   it built** before moving to the next prompt. Don't queue up multiple
   sessions at once — the accounting logic has to be right before the next
   layer builds on it.
4. Commit to git after each session passes (a prompt for this is included at
   the end of each step).

### The files Cline keeps reading — you should already have these

`.clinerules` and `PROGRESS_LOG.md` should already be sitting in your
project root. Cline automatically reads `.clinerules` at the start of every
task — that's your persistent project memory, so you don't have to repeat
the accounting rules each time. `.clinerules` also instructs Cline to update
`PROGRESS_LOG.md` at the end of every session, so if you ever have to switch
tools (rate limit hit, different model, different chat entirely), you paste
the contents of both files into the new tool's first message and it's caught
up instantly.

If you're using a plain chat interface instead of an in-editor agent (i.e.
it does NOT auto-read `.clinerules`), paste the contents of `.clinerules`
and `PROGRESS_LOG.md` yourself as your first message before pasting a
session prompt below.

---

## Session 0 — Product Definition & Repo

**Goal:** freeze scope, create the repo, no code yet beyond scaffolding docs.

```
Read .clinerules and PROGRESS_LOG.md. We are starting Session 0 of the Universal Accounting Learning
& Practice Platform.

1. Initialize a git repository in this folder if one doesn't exist.
2. Create the folder structure described in .clinerules's repository layout
   (empty folders are fine for now, add .gitkeep where needed).
3. Create docs/blueprint-summary.md containing a concise summary of:
   - Product vision (bilingual, beginner-to-advanced accounting learning +
     practice platform, OHADA/IFRS aware)
   - The three modes: Learn, Practice/Bookkeeping, Analyze/AI (AI is future
     scope, note it as "not in MVP")
   - The core accounting chain: transaction -> journal -> ledger -> trial
     balance -> financial statements
   - MVP definition: a user can enter a transaction and trace it through to a
     financial statement, in plain language, with automated tests proving
     accounting integrity
4. Create docs/acceptance-criteria.md listing testable acceptance criteria for
   Sessions 1 through 11 (one short checklist per session, based on what each
   session will build).
5. Create a root .gitignore appropriate for a Python + Node monorepo.
6. Make an initial git commit with message "Session 0: product definition and
   repo skeleton".

Do not write any application code yet.
```

**Before moving on:** open `docs/acceptance-criteria.md` and actually read it —
this is your checklist for the rest of the MVP.

---

## Session 1 — Local Development Environment

**Goal:** React, FastAPI, and PostgreSQL all running and provably talking to
each other, independently, on your machine.

```
Read .clinerules and PROGRESS_LOG.md. Session 1: local development environment.

1. In backend/, set up a Python virtual environment convention (document exact
   commands in README.md — don't assume I have it activated).
2. Create backend/requirements.txt with fastapi, uvicorn, sqlalchemy (or
   sqlmodel), alembic, psycopg2-binary, python-dotenv, pydantic, pytest,
   passlib[bcrypt], python-jose (for JWT later).
3. Create backend/.env.example with placeholders for DATABASE_URL, SECRET_KEY,
   ENV.
4. In frontend/, initialize a React app with Vite and Tailwind CSS configured
   (not create-react-app — Vite is faster for this).
5. Give me exact terminal commands to:
   - create and activate the Python venv
   - install backend dependencies
   - create a local PostgreSQL database and user for this project
   - install frontend dependencies
   - run backend and frontend dev servers
6. Update README.md with a "Getting Started" section containing those exact
   commands, plus a troubleshooting section for common Postgres connection
   errors on Windows/Mac/Linux.
7. Do NOT write me the commands only in chat — put them in README.md so they
   persist.

Stop and wait for me to confirm all three (React, FastAPI, PostgreSQL) are
running before continuing.
```

Run the commands it gives you. Confirm: React dev server loads a blank page,
`uvicorn` starts without errors, and you can connect to the Postgres database
with `psql`. **Do not proceed until all three work.**

---

## Session 2 — Project Skeleton (connect the three)

```
Read .clinerules and PROGRESS_LOG.md. Session 2: project skeleton — connect frontend, backend, and
database.

1. Configure the FastAPI app (backend/app/main.py) with CORS allowing the
   Vite dev server origin.
2. Configure SQLAlchemy/SQLModel database connection using DATABASE_URL from
   .env.
3. Set up Alembic and create an initial (empty) migration to prove the
   pipeline works.
4. Create a GET /health endpoint returning {"status": "ok", "db": <true/false
   based on a real DB ping>}.
5. In frontend, create a simple API service (frontend/src/services/api.js or
   .ts) using fetch, and call /health from the Dashboard/landing page on load,
   displaying the result.
6. Write one backend test (pytest) for the /health endpoint.
7. Commit: "Session 2: project skeleton, frontend-backend-db connected".

Show me how to verify each connection point manually before committing.
```

---

## Session 3 — Authentication + Language Preference

```
Read .clinerules and PROGRESS_LOG.md. Session 3: authentication.

1. Create a `users` table/model: id, email, hashed_password, display_name,
   language_preference (enum: en/fr — leave room for pidgin later per
   .clinerules, but only implement en/fr now), created_at.
2. Implement password hashing with passlib/bcrypt — never store plaintext.
3. Implement POST /auth/register, POST /auth/login (JWT-based), GET /me.
4. Add a dependency for protected routes (require valid JWT).
5. Frontend: build Register and Login pages (mobile-responsive, Tailwind),
   store the JWT appropriately (not localStorage for anything sensitive if
   avoidable — discuss the tradeoff with me briefly in your plan before
   coding), and a basic protected Dashboard page that only loads if
   authenticated.
6. Set up the i18n folder structure (frontend/src/i18n/en.json,
   frontend/src/i18n/fr.json) with a handful of real strings (nav labels,
   login form labels) and a language toggle component in the header that
   switches instantly without a page reload. Wire language_preference to
   persist per-user.
7. Write backend tests: successful registration, duplicate email rejection,
   login success/failure, protected route rejects missing/invalid token.
8. Commit: "Session 3: authentication and language toggle".
```

---

## Session 4 — Workspace & Framework Selection

```
Read .clinerules and PROGRESS_LOG.md. Session 4: organizations/workspaces and OHADA/IFRS framework
selection.

1. Create `organizations` (id, name, owner_user_id, framework [OHADA/IFRS],
   currency, created_at) and `organization_members` (org_id, user_id, role)
   tables.
2. Create `frameworks` and `framework_versions` tables as described in
   .clinerules — even if only one version of each framework exists right now,
   model it so more can be added without a schema change later.
3. API: POST /organizations (create with framework choice), GET
   /organizations (list mine), GET /organizations/{id}.
4. Frontend: after login, if the user has no workspace, show a "Create your
   first workspace" flow — name, framework choice (OHADA or IFRS, with a
   one-line plain-language description of each, no jargon), currency
   (default XAF).
5. Also add a "use a sample demo business" option that creates a pre-seeded
   demo workspace instead of a blank one (seed data comes in Session 5, wire
   the button now).
6. Tests: creating an org attaches the creator as owner; a user cannot access
   another user's organization via the API (authorization test).
7. Commit: "Session 4: workspaces and framework selection".
```

---

## Session 5 — Chart of Accounts

```
Read .clinerules and PROGRESS_LOG.md. Session 5: chart of accounts.

IMPORTANT: per .clinerules, do not fabricate an "official" OHADA chart of
accounts from memory. Build a small, clearly-labeled ILLUSTRATIVE chart of
accounts (10-20 common accounts covering cash, bank, sales, purchases,
expenses, receivables, payables, capital) sufficient to prove the engine
works end-to-end. Mark it in a code comment and in the seed script as
"illustrative demo data — replace with reviewed/licensed official chart
before any real production or compliance use."

1. Create an `accounts` table: id, organization_id, framework, code, name_en,
   name_fr, account_class, parent_account_id (nullable), normal_balance
   (debit/credit), is_system_default (bool), active (bool), description.
2. Seed script producing the illustrative chart of accounts described above,
   for both OHADA-labeled and IFRS-labeled demo sets.
3. API: GET /accounts (scoped to organization), POST /accounts (user-created
   custom account), PATCH /accounts/{id} (activate/deactivate/edit name).
4. Frontend: Chart of Accounts page — list grouped by account_class, search,
   create/edit/deactivate a custom account. Keep it readable for a
   non-accountant (plain labels, not just codes).
5. Validation: account code must be unique within an organization+framework;
   normal_balance must be debit or credit; cannot deactivate an account with
   existing posted transactions (write this rule now, even if the check
   currently always passes since transactions don't exist yet — leave a
   TODO/test placeholder).
6. Tests: seed script runs cleanly; duplicate code rejected; account list is
   scoped per organization (authorization).
7. Commit: "Session 5: chart of accounts with illustrative demo data".
```

---

## Session 6 — First Transaction

```
Read .clinerules and PROGRESS_LOG.md. Session 6: first transaction entry and posting.

1. Create `transactions` and `transaction_lines` tables per .clinerules's
   integrity rules: a transaction has >=2 lines, debit/credit amounts are
   non-negative, and total debits must equal total credits before it can be
   marked posted.
2. Build `transaction_service` and `posting_service` as separate, testable
   modules (not endpoint logic inline) per .clinerules's service separation.
3. API: POST /transactions (create as draft), POST /transactions/{id}/post
   (validate balance, mark posted, make immutable), GET /transactions
   (list, scoped to organization).
4. Frontend: a beginner-friendly "New Transaction" form. Let the user
   describe what happened in plain language first (e.g. "I sold goods for
   50,000 FCFA cash"), then guide them to pick accounts and amounts, then
   show the resulting debit/credit lines before they confirm posting. Show a
   clear "What happened / What this means for your accounts" explanation
   after posting.
5. Enforce at the SERVICE layer (not just the frontend) that an unbalanced
   transaction cannot be posted — reject with a clear error.
6. Tests: balanced transaction posts successfully; unbalanced transaction is
   rejected; posted transaction cannot be edited or deleted (only reversed —
   stub a reversal endpoint even if minimal for now); transaction lines
   reference valid, active accounts only.
7. Commit: "Session 6: first transaction entry and posting logic".
```

---

## Session 7 — Cash Book and Journal

```
Read .clinerules and PROGRESS_LOG.md. Session 7: cash book and journal views.

1. Build the Journal as a read view over posted transactions/transaction_lines
   with the fields from the blueprint: date, reference, description, account
   number, account name, debit, credit, narration, source, posting status,
   created by/timestamp.
2. Build a Cash Book view filtering to cash/bank account movements
   specifically.
3. API: GET /journal-entries (filterable by date range, account, reference),
   GET /cashbook (same, filtered to cash/bank accounts).
4. Frontend: Journal page and Cash Book page with date filters and a
   drill-down link from each row back to the originating transaction detail.
5. Tests: journal totals for a period match the sum of posted transaction
   lines in that period; cash book only shows cash/bank-account movements.
6. Commit: "Session 7: cash book and journal".
```

---

## Session 8 — General Ledger

```
Read .clinerules and PROGRESS_LOG.md. Session 8: general ledger.

1. Build `ledger_service`: for a given account and period, compute opening
   balance, debit movements, credit movements, and running/closing balance
   from posted journal lines. Per .clinerules, derive this from posted data —
   do not store a separately-maintained ledger balance that can drift out of
   sync.
2. API: GET /ledger/{account_id}?from=&to=
3. Frontend: General Ledger page — select an account, see opening balance,
   chronological movements, running balance, with drill-down back to the
   journal/transaction.
4. Tests: ledger closing balance for a period equals opening balance + debit
   movements - credit movements (or + credit - debit depending on normal
   balance); ledger for an account with no activity shows opening = closing.
5. Commit: "Session 8: general ledger".
```

---

## Session 9 — Trial Balance

```
Read .clinerules and PROGRESS_LOG.md. Session 9: trial balance.

1. Build `trial_balance_service`: for a given organization and period,
   compute every account's debit or credit balance from the ledger logic,
   and total debits vs total credits.
2. API: GET /trial-balance?organization_id=&as_of=
3. Frontend: Trial Balance page — account code, name, debit balance, credit
   balance, totals row, clear pass/fail indicator if totals don't match
   (they must always match for posted data — if they don't, that's a bug to
   surface loudly, not hide), drill-down to ledger per account.
4. Tests: trial balance total debits == total credits for a range of seeded
   transaction scenarios; an account with zero activity doesn't appear (or
   appears with zero, your choice — document which); period filtering
   works correctly.
5. Commit: "Session 9: trial balance".
```

---

## Session 10 — Financial Statements

**The blueprint calls this your first real milestone. Do not rush it.**

```
Read .clinerules and PROGRESS_LOG.md. Session 10: financial statements, generated FROM the ledger
— never manually entered.

1. Build `financial_statement_service`: generate a basic Income Statement
   (revenue - expenses) and a basic Statement of Financial Position
   (assets = liabilities + equity) purely from posted trial-balance-level
   data, mapped by account_class.
2. API: GET /reports/income-statement?organization_id=&period=, GET
   /reports/financial-position?organization_id=&as_of=
3. Frontend: Financial Statements page showing both statements, clearly
   labeled with the organization's chosen framework (OHADA/IFRS), with
   drill-down from each line back to the underlying accounts/ledger.
4. Add a plain-language summary above each statement (e.g. "You received
   X, spent Y, and your business made a profit of Z this period") — per
   .clinerules's UX principle of explaining in plain language before jargon.
5. Tests: statement of financial position balances (assets = liabilities +
   equity) for known seeded scenarios; income statement total matches
   revenue-account totals minus expense-account totals from the trial
   balance; statements only include posted (not draft) transactions.
6. Commit: "Session 10: financial statements".

After this commit, walk me through manually: create a workspace, post 3-4
varied transactions, and trace them through journal -> ledger -> trial
balance -> financial statement in the running app. Tell me if anything looks
inconsistent before we go further.
```

**Stop here and actually do the manual walkthrough it describes.** This is
the blueprint's own "first major milestone" gate (Section 51) — a user can
create a workspace, post a transaction, and see it flow correctly all the
way to a financial statement, with English/French toggle working and tests
covering the core rules.

---

## Session 11 — Learning Engine (basic)

```
Read .clinerules and PROGRESS_LOG.md. Session 11: basic learning engine — this closes out the MVP
scope per the blueprint (Sessions 0-11).

1. Create `lessons`, `lesson_sections`, `questions`, `answers`, `attempts`,
   `progress` tables — kept simple, no AI generation yet (that's future
   scope, explicitly out of MVP).
2. Seed 3-5 short lessons covering: accounting basics, the accounting
   equation, debit and credit, journal entries, reading a trial balance —
   written in plain language, in English and French.
3. Each lesson ends with 2-3 simple multiple-choice or short-answer
   questions with stored correct answers (not AI-checked yet — straight
   comparison).
4. API: GET /learning/lessons, GET /learning/lessons/{id}, POST
   /learning/attempts (submit an answer, get scored, record progress).
5. Frontend: Learn page (lesson list with progress indicators), Lesson
   detail page (content -> try a question -> feedback), tied to the
   language toggle from Session 3.
6. Bonus per the blueprint's example lesson loop: on at least one lesson,
   let the user's practice answer actually post a real transaction into
   their demo workspace so they see the effect in the ledger/trial balance
   they already built — this connects Learn Mode to Practice Mode instead
   of leaving them separate.
7. Tests: correct/incorrect answer scoring; progress is recorded per user;
   lesson content respects language toggle.
8. Commit: "Session 11: basic learning engine — MVP complete".

Give me a final summary comparing what we built against
docs/acceptance-criteria.md from Session 0, and flag anything that's
incomplete or deviates from the original acceptance criteria.
```

---

## What you have after Session 11

Per the blueprint's own MVP definition (Section 45–46): a user can register,
pick a language, create a workspace with an OHADA or IFRS framework, use an
illustrative chart of accounts, enter a transaction in plain language, see it
posted through the journal and ledger, generate a trial balance and basic
financial statements, and work through a few basic lessons — all covered by
automated tests, all running locally, no AI required.

**Do not start Session 12+ (full bilingual content, testing/UAT pass, AI
tutor, payments, analytics, OCR) until you've used this yourself and ideally
shown it to one accounting-literate person and one complete beginner**, per
the blueprint's Session 13/14 guidance — that user feedback should shape
what Session 12 onward actually prioritizes.

---

## Notes on where I adjusted or added to the blueprint

- **Testing moved earlier.** The blueprint places formal testing at Session
  13, but its own MVP checklist requires "tests proving accounting
  integrity." I built a test into every session above instead of deferring
  it — retrofitting tests onto seven sessions of untested accounting logic
  at once is much riskier than writing them as you go.
- **Language toggle moved into Session 3.** The MVP checklist (Section 45)
  lists "English/French toggle" as required, but the session plan doesn't
  introduce it until Session 12. I moved the i18n skeleton and toggle into
  Session 3 (auth/profile) since it's cheap to add early and expensive to
  retrofit into every page later.
- **.clinerules as persistent memory.** The blueprint doesn't mention agentic
  coding tools at all — this file is the mechanism that keeps Cline
  from drifting off the blueprint's rules (deterministic engine, no
  fabricated OHADA chart, framework separation) across 12 separate sessions.
- **Learn/Practice connection in Session 11.** The blueprint's "example
  lesson loop" (Section 17) already describes posting a lesson's example
  into the accounting engine — I made that an explicit deliverable rather
  than an optional nice-to-have, since it's the one thing that makes this
  product different from a plain bookkeeping app or a plain course site.
- **Illustrative chart of accounts, explicitly labeled.** The blueprint
  warns (Section 9) not to fabricate an official OHADA chart from memory.
  I made that warning a literal instruction inside the Session 5 prompt so
  the coding agent doesn't quietly generate one anyway — this is the single
  easiest place for an AI agent to overstep the blueprint's own caution.
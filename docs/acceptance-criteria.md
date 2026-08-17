# MVP Acceptance Criteria (Sessions 1–11)

> Created in **Session 0**. This is the living checklist for the MVP. Each
> session's checklist is based on what the session builds. Read this before
> moving on after every session. At the end of Session 11 we compare what we
> built against this file.

---

## Session 1 — Local Development Environment
- [ ] Backend Python virtual environment documented with exact commands in README.md
- [ ] backend/requirements.txt contains fastapi, uvicorn, sqlalchemy, alembic, psycopg2-binary, python-dotenv, pydantic, pytest, passlib[bcrypt], python-jose
- [ ] backend/.env.example created with DATABASE_URL, SECRET_KEY, ENV placeholders
- [ ] frontend/ is a Vite + React + Tailwind app (not create-react-app)
- [ ] README.md "Getting Started" has exact commands for venv, deps, Postgres setup, running both servers
- [ ] README.md has a troubleshooting section for Postgres connection errors
- [ ] MANUAL: React dev server loads, `uvicorn` starts, `psql` connects to the DB

## Session 2 — Project Skeleton (connect the three)
- [ ] FastAPI app (backend/app/main.py) with CORS for the Vite dev origin
- [ ] SQLAlchemy/SQLModel DB connection from DATABASE_URL in .env
- [ ] Alembic configured with an initial (empty) migration that runs
- [ ] GET /health returns {"status":"ok","db":<true/false>} with a real DB ping
- [ ] frontend/src/services/api.js calls /health and the dashboard displays the result
- [ ] Backend pytest for the /health endpoint (incl. db ping)
- [ ] MANUAL: each connection point (frontend↔backend, backend↔db) verifiable

## Session 3 — Authentication + Language Preference
- [ ] `users` table: id, email, hashed_password, display_name, language_preference (en/fr), created_at
- [ ] Passwords hashed with passlib/bcrypt (never plaintext)
- [ ] POST /auth/register, POST /auth/login (JWT), GET /me
- [ ] Protected-route dependency (requires valid JWT)
- [ ] Frontend Register + Login pages, mobile-responsive, JWT stored safely (tradeoff decided)
- [ ] Protected Dashboard loads only when authenticated
- [ ] i18n structure: frontend/src/i18n/{en,fr}.json + working language toggle with no reload
- [ ] language_preference persisted per user
- [ ] Tests: register success, duplicate email rejected, login success/failure, protected route rejects bad token

## Session 4 — Workspace & Framework Selection
- [ ] `organizations` (id, name, owner_user_id, framework[OHADA/IFRS], currency, created_at) and `organization_members` (org_id, user_id, role)
- [ ] `frameworks` and `framework_versions` tables modeled for future additions
- [ ] API: POST /organizations, GET /organizations, GET /organizations/{id}
- [ ] First-workspace creation flow: name, framework (plain-language descriptions), currency (default XAF)
- [ ] "use a sample demo business" option wired now (seed data comes in Session 5)
- [ ] Tests: creator becomes owner; cross-org access rejected (authorization)

## Session 5 — Chart of Accounts
- [x] `accounts` table: id, organization_id, framework, code, name_en, name_fr, account_class, parent_account_id, normal_balance, is_system_default, active, description
- [x] Seed script for a small ILLUSTRATIVE chart (10–20 accounts) for BOTH OHADA- and IFRS-labeled sets
- [x] Seed data clearly labeled "illustrative demo data — replace before production/compliance use"
- [x] API: GET /accounts (scoped), POST /accounts, PATCH /accounts/{id}
- [x] Frontend Chart of Accounts page: grouped by class, search, create/edit/deactivate; plain labels
- [x] Validation: code unique per org+framework; normal_balance ∈ {debit, credit}; cannot deactivate account with posted transactions (rule + placeholder)
<br>
> **Note:** Session 5's illustrative chart (above) is superseded by **Session 6b**, which
> replaces it with the real OHADA SYSCOHADA 2017 révisé structure and an editable IFRS
> template. The Session 5 items remain historically checked (they were built in S5) but the
> seed data, structure, and frontend rendering were upgraded in S6b.

## Session 6b — OHADA/IFRS standards-compliant chart of accounts with autocomplete
- [x] Migration `0006_add_ohada_class_number` adds nullable `ohada_class_number` (Integer 1–9) to `accounts`; the simplified `account_class` enum (asset/liability/equity/revenue/expense) is retained for normal-balance logic only.
- [x] OHADA workspaces seeded with a **representative real SYSCOHADA (2017 révisé)** structure: all 9 classes, real hierarchical codes (2/3/4-digit via `parent_account_id`, 3+ levels deep in the common sub-classes), `ohada_class_number` = first digit; Class 9 marked supplementary (off-balance-sheet/CAGE), not part of core statements. Source: `docs/ohada-ifrs-source-reference.md` only — NOT fabricated from memory. Labeled as a representative subset, not the full ~900-line official list.
- [x] IFRS workspaces seeded with an **editable IAS-1-aligned starting template** under the 5 plain classes (no mandated IFRS chart per IAS 1); `ohada_class_number` stays NULL.
- [x] Demo workspaces auto-seeded with their framework's structure on creation; `scripts/seed_coa.py` idempotent (safe to re-run).
- [x] API unchanged (GET/POST/PATCH /accounts, org-scoped) but now serves real hierarchical OHADA data; PATCH still only edits name_en/name_fr/active.
- [x] Frontend Chart of Accounts page: hierarchical tree (indented by depth via `parent_account_id`), OHADA class badges + class number column, framework-aware demo notice (real SYSCOHADA vs editable template vs legacy Session-5 data).
- [x] Bidirectional `AccountLookup` component (and `accountLookup.js` util): search by code OR name (EN + FR), scoped to the org's own accounts (no cross-workspace leakage). Wired into the create form to auto-fill parent + names.
- [x] Existing Session 5/6 data preserved: legacy flat chart left as-is and labelled; `ohada_class_number` nullable so old rows remain valid; posted transactions (referencing accounts by id) untouched.
- [x] Tests: OHADA seed produces correct 9-class hierarchy/parent links/class numbers; IFRS template seeds + editable; autocomplete matches by code or name and stays within-org only; legacy compatibility (no breakage of existing S5/S6 demo data); 46 backend tests pass; `npm run build` rc=0.
- [x] Tests: seed runs clean, duplicate code rejected, list scoped per org

## Session 6 — First Transaction
- [x] `transactions` + `transaction_lines` tables (≥2 lines, non-negative amounts, balance enforced before posted)
- [x] Separate `transaction_service` and `posting_service` modules
- [x] API: POST /transactions (draft), POST /transactions/{id}/post (validate, mark posted, immutable), GET /transactions
- [x] Frontend New Transaction form: plain-language description → pick accounts/amounts → review D/C lines → confirm
- [x] "What happened / what this means" explanation after posting
- [x] SERVICE-layer rejection of unbalanced posting with clear error
- [x] Tests: balanced posts; unbalanced rejected; posted can't be edited/deleted (reversal stub); lines reference valid, active accounts

## Session 6c — OHADA-standard journal entry UI + account selector bug fix
- [x] Bug fixed: transaction account selector now uses the Session 6b `AccountLookup` (compact mode) instead of a plain `<select>`. Root cause (confirmed via manual check of existing demo orgs + a fresh demo OHADA org): the plain select was never upgraded after 6b's account-model changes, showed all accounts (incl. inactive, which the backend rejects) with no search/hierarchy, and degraded to an empty-looking dropdown due to a number-vs-string controlled-select value mismatch.
- [x] New Transaction form redesigned as a real OHADA journal-entry grid: Date | N° compte (AccountLookup autocomplete) | Intitulé (auto-filled, read-only) | Libellé | Débit | Crédit — debit lines first, credit lines after, totals equal before posting.
- [x] Plain-language "what happened?" description step kept above the grid; running debit/credit totals + balanced/unbalanced indicator update live as the user types.
- [x] Service-layer balance enforcement unchanged (not weakened) — posting_service untouched.
- [x] Mobile-responsive: desktop = 12-column grid aligned with a header row; phone-width = each line stacks into a card (no horizontal scroll).
- [x] Account lookup is within-org only (reuses the org-scoped account list); only active accounts are selectable.
- [x] Date field auto-fills to today and is editable (UI-only; backend uses created_at — a transaction_date column is deferred to a future session).
- [x] Tests: new `txnCalculations.test.mjs` (14 checks: live totals, balanced check, canPost, payload mapping); `accountLookup.test.mjs` unchanged; `npm run build` rc=0 (43 modules); backend pytest unchanged at 46 passed; end-to-end fresh demo OHADA org verification passed.

## Session 7 — Cash Book and Journal
- [ ] Journal read view: date, reference, description, account number/name, debit, credit, narration, source, posting status, created by/timestamp
- [ ] Cash Book view filtered to cash/bank movements
- [ ] API: GET /journal-entries (filters), GET /cashbook
- [ ] Frontend Journal + Cash Book pages with date filters and drill-down to transaction
- [ ] Tests: journal totals match posted lines in period; cash book only cash/bank

## Session 8 — General Ledger
- [ ] `ledger_service`: opening balance, debit movements, credit movements, running/closing balance — derived from posted lines, not stored
- [ ] API: GET /ledger/{account_id}?from=&to=
- [ ] Frontend General Ledger page: select account, opening, movements, running balance, drill-down
- [ ] Tests: closing = opening + movements (per normal balance); no-activity account shows opening == closing

## Session 9 — Trial Balance
- [ ] `trial_balance_service`: every account's debit/credit balance for a period, total debits vs credits
- [ ] API: GET /trial-balance?organization_id=&as_of=
- [ ] Frontend Trial Balance page: code, name, debit, credit, totals row, pass/fail indicator, drill-down to ledger
- [ ] Tests: total debits == total credits across seeded scenarios; zero-activity account handling documented; period filtering correct

## Session 10 — Financial Statements (first milestone)
- [ ] `financial_statement_service`: Income Statement + Statement of Financial Position from trial-balance data by account_class
- [ ] API: GET /reports/income-statement?period=, GET /reports/financial-position?as_of=
- [ ] Frontend statements page: both statements, framework-labeled, drill-down per line
- [ ] Plain-language summary above each statement
- [ ] Tests: SOFP balances (A = L + E); income statement = revenue − expenses; only posted transactions included
- [ ] MANUAL WALKTHROUGH: create workspace → post 3–4 varied transactions → trace through journal → ledger → trial balance → statements → language toggle works → tests cover core rules

## Session 11 — Learning Engine (basic) — MVP complete
- [ ] Tables: lessons, lesson_sections, questions, answers, attempts, progress (no AI)
- [ ] Seed 3–5 plain-language lessons (basics, accounting equation, debit/credit, journal entries, reading a trial balance) in English and French
- [ ] Each lesson ends with 2–3 MC/short-answer questions with stored answers (straight comparison)
- [ ] API: GET /learning/lessons, GET /learning/lessons/{id}, POST /learning/attempts
- [ ] Frontend Learn page (lesson list + progress) and Lesson detail (content → question → feedback) tied to language toggle
- [ ] At least one lesson posts a REAL transaction into the demo workspace (connects Learn → Practice)
- [ ] Tests: correct/incorrect scoring, progress recorded per user, lesson content respects language
- [ ] FINAL: compare build against this file; flag deviations/incomplete items

---

## Cross-cutting MVP requirements (from blueprint)
- [ ] Responsive web app usable on a phone-width browser from the start
- [ ] English/French toggle works app-wide without reload
- [ ] Every posted transaction balances; enforced at service/db layer
- [ ] Posted records immutable / corrected via reversing entries
- [ ] Automated tests prove accounting integrity (Sessions 2–11)
- [ ] Illustrative chart of accounts, clearly labeled, never a fabricated "official" OHADA chart

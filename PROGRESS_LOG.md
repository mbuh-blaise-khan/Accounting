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

**Last completed session:** Session 6 — First Transaction Entry & Posting
**Next session to run:** Session 7 — Cash Book and Journal
**Blockers / open questions:** None outstanding.

---

## Session Log

### Session 6 — First Transaction Entry & Posting
- Status: DONE
- Date completed: 2026-08-14
- What was built:
  - `transactions` + `transaction_lines` tables (migration `0005`). Transaction:
    org, plain-language description, status (draft/posted/reversed), posted_at,
    created_by, created_at. Line: txn FK (cascade), account FK, non-negative
    debit/credit (Numeric(16,2)), DB check constraints (amounts >= 0; a line
    cannot be both zero). `TransactionStatus` enum added.
  - `app/services/transaction_service.py`: create_draft_transaction (org-scoped;
    enforces >=2 lines, non-negative amounts, exactly-one-side-per-line, lines
    reference known + active accounts in the same org), list_transactions,
    get_transaction (org-scoped), assert_editable (immutability guard), and a
    serializer that denormalizes account code/name onto line output.
  - `app/services/posting_service.py`: `post_transaction` RE-VERIFIES the
    balance IN THE SERVICE LAYER (sum debits == sum credits) and rejects an
    unbalanced draft with a clear 400 before marking it posted + posted_at
    (immutable thereafter). `reverse_transaction` STUB: only a posted tx can be
    reversed (409 otherwise); marks status 'reversed'. Real offsetting entries
    deferred to the corrections work later.
  - API (`api/routes/transactions.py`): POST /transactions (draft, 201), GET
    /transactions?organization_id=, POST /transactions/{id}/post,
    POST /transactions/{id}/reverse. All org-scoped (cross-org → 404). Wired
    into api/router.py.
  - Closed Session-5 handoff: `account_service.has_posted_transactions()` is now
    REAL — joins transaction_lines→transactions where status != draft, so
    deactivation of an account used in a posted tx is blocked (409). Updated the
    old placeholder test and added blocking/draft scenarios.
  - Frontend: `NewTransactionPage.jsx` beginner flow — plain-language
    description → pick account + side (debit/credit) + amount per line → live
    running totals with balanced/unbalanced indicator → review the D/C lines →
    confirm post (UI only enables posting when balanced; backend independently
    enforces) → "What happened / What this means for your accounts" success
    screen (uses account normal_balance to say an account went up/down).
    `api.js` +createTransaction/fetchTransactions/postTransaction. DashboardPage
    now shows a workspace shell with tabs (Home / Chart of Accounts / New
    Transaction) + cards. i18n EN/FR added.
  - Tests (test_transactions.py, 14 new): draft creation; balanced posts;
    unbalanced REJECTED at service (400, "balanced" error); >=2 lines required;
    line cannot be both sides/neither; lines must reference known + active
    accounts (inactive → 422); posted cannot be re-posted (409); immutability
    guard rejects posted (assert_editable raises 409) while drafts stay
    editable; reversal of a posted tx; draft/re-reversed reversal rejected (409);
    list scoped per org; deactivation blocked once posted (409) but allowed for
    draft-only usage. conftest cleanup now also deletes transaction tables.
- Verification:
  - `pytest app/tests` → 45 passed (2.79s) (30 prior + 15 new/updated).
  - Live: `alembic upgrade head` applied 0005 on real Postgres (rc=0).
  - `npm run build` → rc=0 (40 modules).
- What Session 7 needs to know:
  - Transactions carry status (posted/reversed) + posted_at and lines link to
    accounts, so the journal read view can be built directly on top.
  - Reversal is still a stub (marks reversed only) — real reversing entries are
    part of the corrections work in a later session.
  - No date column on transactions yet; decide whether the journal/cashbook
    needs an entry date (then add it) or will use created_at for now.

### Session 5 — Chart of Accounts
- Status: DONE
- Date completed: 2026-08-14
- What was built:
  - `accounts` table (migration `0004`): id, organization_id (FK), framework
    (Enum OHADA/IFRS), code, name_en, name_fr, account_class (plain classes:
    asset/liability/equity/revenue/expense), parent_account_id (nullable
    self-FK), normal_balance (debit/credit), is_system_default, active,
    description, created_at. Unique constraint (organization_id, framework,
    code) enforces "code unique within org+framework".
  - New enums: `AccountClass`, `NormalBalance` (models/enums.py); new model
    `app/models/account.py`.
  - `app/services/account_service.py`: membership-scoped `list_accounts`,
    `create_custom_account` (rejects duplicate code 409 + mismatched framework
    400 + bad parent 400), `update_account` (edit names / toggle active) with
    the "cannot deactivate an account with posted transactions" rule wired to
    `has_posted_transactions()` — a PLACEHOLDER that returns False until
    Session 6 adds transactions (todo noted).
  - ILLUSTRATIVE/DEMO chart: `ILLUSTRATIVE_CHART` constant (18 plain-language
    accounts: cash, bank, receivables, inventory, equipment, payables, loans,
    capital, retained earnings, sales, service revenue, purchases, rent,
    salaries, utilities, advertising, supplies, other expenses). normal_balance
    is derived deterministically from account class. Clearly labeled
    "illustrative demo data — replace with a reviewed/licensed official chart
    before any real production or compliance use" (in code comments + seed
    script + UI banner + acceptance criteria). NOT an official OHADA/IFRS chart.
  - `seed_illustrative_chart()` service fn + `scripts/seed_coa.py` runner
    (`python -m scripts.seed_coa <org_id> [--framework ...]`, idempotent).
    Demo workspaces are now auto-seeded on creation (organization_service
    create_organization calls seed when is_demo=True) — fulfills Session 4's
    promised hook.
  - API (protected, org-scoped): GET /accounts?organization_id=, POST
    /accounts, PATCH /accounts/{id}?organization_id=. Cross-org access → 404
    (not 403). Added to api/router.py.
  - Frontend: `services/api.js` (+fetchAccounts/createAccount/updateAccount),
    new `pages/ChartOfAccountsPage.jsx` (grouped by class, search, create /
    edit / deactivate, plain labels + "System"/"Inactive" badges, EN/FR
    names), DashboardPage opens a workspace's chart via an "Open chart of
    accounts" button; i18n EN/FR strings added. Mobile-responsive Tailwind.
  - Tests (test_accounts.py, 11 new): seed runs clean + idempotent; demo org
    auto-seeds; duplicate code rejected (409); same code allowed across
    frameworks; mismatched framework rejected; invalid normal_balance rejected
    (422); account list scoped per org (cross-org 404 + empty for others);
    PATCH edit name + toggle active; deactivation placeholder rule; custom
    account not system default; unauth 401. conftest cleanup now also deletes
    `accounts`.
  - DECISIONS: (1) Same illustrative set for every framework label — the
    `framework` column tags OHADA vs IFRS context rather than differing codes;
    honest & safe given "never fabricate official chart". (2) account_class
    uses plain non-accountant classes (asset/liability/equity/revenue/expense)
    rather than numbered OHADA classes 1-8. (3) normal_balance auto-derived
    from class in seed (deterministic).
- Verification:
  - `pytest app/tests` → 30 passed (1.48s).
  - `alembic upgrade head --sql` → valid SQL for `accounts`.
  - Live: `alembic upgrade head` applied 0004 on real Postgres (rc=0).
  - Live: `seed_coa 2` → 18 rows on demo IFRS org; accounts present with
    correct normal_balance + is_system_default.
  - `npm run build` → rc=0 (39 modules).
- What Session 6 needs to know:
  - Account codes/classes established; `accounts.active` + `normal_balance`
    available for posting. `has_posted_transactions(account_id)` in
    account_service is a placeholder — implement it in Session 6 (join
    transaction_lines → transactions where status='posted') so the
    deactivation rule actually blocks once transactions exist, then extend
    its placeholder test to assert a 409.


### Session 4 — Workspace & Framework Selection
- Status: DONE
- Date completed: 2026-08-10
- What was built:
  - `organizations` table (migration `0003`): id, name, owner_user_id (FK users),
    framework (Enum OHADA/IFRS), currency (default XAF), is_demo (bool), created_at.
  - `organization_members`: org_id/user_id/role (owner|member), unique (org,user).
  - `frameworks` + `framework_versions`: generic registry (code, name,
    description_en/fr, is_active; versions with version_label/is_current) so new
    frameworks or versions need no schema change. `frameworks`/`organization`
    share `FrameworkCode` enum (models/enums.py).
  - `app/models/enums.py` (FrameworkCode, MembershipRole).
  - Services: `framework_service.ensure_default_frameworks()` (idempotent seed:
    OHADA "SYSCOHADA (revision 2017)", IFRS "IFRS consolidated (2023)", each with
    EN/FR plain-language descriptions) + `scripts/seed_frameworks.py` runner;
    `organization_service` (create -> always attaches creator as OWNER member,
    list-scoped-to-user, get-with-membership-check raising 404).
  - API (protected): POST /organizations (201), GET /organizations, GET
    /organizations/{id}, GET /frameworks (with versions). Cross-org access
    returns 404 (not 403) to avoid leaking existence.
  - Frontend: services/api.js (+fetchOrganizations/fetchOrganization/
    createOrganization/fetchFrameworks), components/CreateWorkspace.jsx
    (name, framework radio with plain-language description per lang, currency
    default XAF, and a "Use a sample demo business" button that creates an
    is_demo workspace — account seed data lands in Session 5), DashboardPage
    rewritten to load orgs+frameworks, show the create flow when empty, else
    list workspaces; i18n strings EN/FR added.
  - Tests (test_organizations.py): creator becomes owner member; default
    currency XAF; list scoped to my memberships; cross-org access 404 + not in
    list; demo flag; frameworks listed with descriptions + current version;
    unauthenticated 401. (Test DB also seeds frameworks via conftest.)
  - DECISION: bcrypt rounds made configurable (BCRYPT_ROUNDS=4 default) — keeps
    local dev/tests fast; raise to >=12 before production. (Symptom fixed:
    passlib/bcrypt slowness was timing out test runs.)
- Verification:
  - `pytest app/tests` → 19 passed (1.55s).
  - `alembic upgrade head` → applied 0003 (rc=0); `seed_frameworks` OK (2 rows).
  - Live smoke vs real Postgres: /frameworks ['OHADA','IFRS']; create org 201
    (OHADA, XAF, owner set); list 200 (1); get 200; second user cross-org 404;
    second user list empty; test data cleaned up.
  - `npm run build` → rc=0 (38 modules).
- What Session 5 needs to know:
  - Organizations exist; `is_demo` flag marks workspaces for the demo chart seed.
  - Add the demo/illustrative chart of accounts seed (clearly labeled as
    illustrative — never an "official" fabricated OHADA chart), accounts table,
    GET/POST/PATCH /accounts, and the Chart of Accounts frontend page.
  - Framework registry is seeded; `frameworks` FK available for accounts rows.
  - Existing users: run `python -m scripts.seed_frameworks` after fresh DB.
### Session 3 — Authentication + Language Preference

- Status: DONE
- Date completed: 2026-08-10
- What was built:
  - `users` table (migration `0002`) + `app/models/user.py`: id, email, hashed_password,
    display_name, language_preference (SQLAlchemy Enum en/fr, native_enum=False so
    "pidgin"/others can be added later without a schema change), created_at.
  - `app/core/security.py`: password hashing + JWT create/decode.
    IMPORTANT DECISION: uses the `bcrypt` library DIRECTLY, not passlib —
    passlib 1.7.4 is incompatible with installed bcrypt 4.x (its backend probe
    passes a >72-byte secret that bcrypt 4.x rejects, crashing hashing). Direct
    bcrypt is stable. Passwords never stored in plaintext (bcrypt `$2b$` hashes).
  - `POST /auth/register`, `POST /auth/login`, `POST /auth/logout` (auth router,
    prefix /auth). Register/login set the JWT as an **httpOnly cookie**.
  - `GET /me`, `PATCH /me` (users router, no prefix, per spec). PATCH persists
    language_preference / display_name.
  - `app/api/deps.py`: `get_current_user` protected-route dependency — reads JWT
    from `Authorization: Bearer` header OR the httpOnly `access_token` cookie,
    decodes, loads user, raises 401 otherwise.
  - Frontend i18n: `src/i18n/{en,fr}.json` (nav + login + register + dashboard +
    status strings), `src/i18n/index.jsx` (LanguageProvider + useLanguage + t),
    `src/components/LanguageToggle.jsx` (instant EN<->FR switch, no reload).
  - Frontend auth: `src/services/api.js` (register/login/logout/me/updateMe with
    credentials:'include'), `src/context/AuthContext.jsx` (reloadUser on mount,
    login/register/logout/setUserLanguage), pages LoginPage/RegisterPage/HomePage/
    DashboardPage (mobile-responsive, Tailwind), App.jsx wires providers + a
    lightweight view switch; **Dashboard only renders when authed**.
  - Language toggle persists per-user: setUserLanguage → PATCH /me.
  - Tests (`app/tests/test_auth.py`, SQLite in-memory isolation via conftest):
    register success + cookie, password not plaintext ($2b$ hash), duplicate email
    409, login success, login wrong password 401, login unknown email 401, /me with
    valid token 200, /me missing token 401, /me invalid token 401.
  - README + backend/.env.example updated (JWT settings, auth endpoint table,
    httpOnly-cookie note).
- Security/config decision (user-directed): JWT stored in an **httpOnly cookie**
  set by backend rather than localStorage — reason: httpOnly cookies are not
  readable by frontend JS, so a script-injection/XSS bug cannot exfiltrate the
  token; safer default for this stage. Frontend sends it via credentials:'include'.
- Verification:
  - `pytest app/tests` → 12 passed.
  - `alembic upgrade head` → applied 0002 (rc=0).
  - Live end-to-end smoke vs real Postgres: register 200+cookie, /me 200,
    /me w/o token 401, duplicate 409, login wrong pw 401, login ok 200+cookie;
    test user cleaned up.
  - `npm run build` → rc=0 (37 modules).
- What Session 4 needs to know:
  - Auth dependency `get_current_user` (app.api.deps) ready for protected org routes.
  - `Base.metadata` includes users; new tables added to app/models and auto-migrated
    via `python -m alembic revision --autogenerate -m "..."`.
  - i18n + LanguageProvider are app-wide; add new strings to en.json/fr.json.
  - Frontend has no router dependency yet — Session 4 may add pages/views through
    the existing lightweight view switch or introduce react-router.
### Session 2 — Project Skeleton (frontend-backend-db connected)

- Status: DONE
- Date completed: 2026-08-10
- What was built:
  - Package structure: added `__init__.py` to `backend`, `backend/app` and all
    backend subpackages so `app.*` is importable.
  - `backend/app/core/config.py` — pydantic-settings `Settings` reading
    `backend/.env` (DATABASE_URL, SECRET_KEY, ENV, FRONTEND_ORIGIN) with dev
    defaults; path resolved from the file so it works from any cwd.
  - `backend/app/core/database.py` — SQLAlchemy 2.0 engine (pool_pre_ping),
    `SessionLocal`, declarative `Base`, `get_db` dependency, and
    `check_db_connection()` (SELECT 1 probe) used by /health.
  - `backend/app/main.py` — FastAPI app with CORS for the Vite origin
    (http://localhost:5173) + a root "/" route.
  - `backend/app/api/router.py` + `api/routes/health.py` — `GET /health`
    returns `{"status":"ok","db":<bool from real DB ping>}`.
  - Alembic wired: `backend/alembic.ini`, `alembic/env.py` (loads DATABASE_URL
    from settings, wires Base.metadata), `script.py.mako`, and an EMPTY initial
    migration `versions/0001_initial_empty.py`. `alembic upgrade head` applied
    successfully (rc=0) — proves the migration pipeline + DB connection.
  - Frontend: `frontend/src/services/api.js` (fetch-based client, `fetchHealth`,
    API_BASE from `VITE_API_BASE` default http://localhost:8000); `App.jsx`
    rewritten to call `/health` on load and show API + DB status.
  - `backend/app/tests/test_health.py` — 3 tests (db up / db down via
    monkeypatch, and a live-DB integration check that skips if unreachable).
  - README: updated backend run/test/migrate commands (run from `backend/`),
    added /health endpoint info.
- Verification performed (all passed):
  - `pytest app/tests` → 3 passed.
  - `alembic upgrade head` → rc=0 (created alembic_version in Postgres).
  - Live server boot via uvicorn → "Application startup complete".
  - `/health` via TestClient → HTTP 200 `{"status":"ok","db":true}` (real DB ping).
  - `npm run build` → BUILD_RC=0 (28 modules; Tailwind compiled).
- Decisions made:
  - Run backend (uvicorn, pytest, alembic) from the `backend/` directory so
    imports are `app.*` (not `backend.app.*`). Documented in README.
  - SQLAlchemy 2.0 declarative (`DeclarativeBase`) for all models.
  - `/health` uses a live `SELECT 1` round-trip via `check_db_connection()`.
  - Test the /health db flag by calling through the module
    (`database.check_db_connection()`) so monkeypatch works.
- What Session 3 needs to know:
  - Models live in `app/models`, import `Base` from `app.core.database`.
  - New migrations: `cd backend && python -m alembic revision --autogenerate -m "..."`.
  - Add routers: create `app/api/routes/xxx.py` and include in `app/api/router.py`.
  - Session 3 adds `users` table + auth (register/login/me), passlib[bcrypt] +
    python-jose JWT, i18n skeleton + language toggle, protected Dashboard, and
    auth tests.

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

### Session 5 — Chart of Accounts
- Status: DONE (see full entry at the top of the session log)

### Session 6 — First Transaction
- Status: DONE (see full entry at the top of the session log)

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
  Session 5) → latest Session 5 entry above: same plain-language set for both
  OHADA/IFRS labels; never claims to be official.
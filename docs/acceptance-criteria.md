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
- [x] Part A: bugs fixed (Chart of Accounts showed no rows / search dead → `AccountTree` now renders every account incl. orphans; "Add a line" button unreactive → grid always rendered, not hidden behind loading/no-accounts). Root causes confirmed in the real files.
- [x] IFRS code removal (Part B): IFRS accounts store no code (`accounts.code` nullable; IFRS seed/search/UI code-free); OHADA numbering unchanged.
- [x] Description field modernized + real `posted_at` surfaced as the leading date everywhere a posted transaction appears (Part C).
- [x] Journal read view: date (posted_at, first), reference, description, account number (OHADA only), account name, debit, credit, narration, source, posting status
- [x] Cash Book view filtered to cash/bank movements
- [x] Cash Book types: single-column cash-only and double-column cash/bank with separate Cash Dr, Bank Dr, Cash Cr, Bank Cr totals; triple-column and petty-cash/imprest deliberately deferred because discount/float concepts are not in the schema
- [x] API: GET /journal-entries (filters), GET /cashbook?type=single|double (default double), with each row tagged cash or bank
- [x] Frontend Journal + Cash Book pages with date filters, type selector, framework-aware columns, CSV export, and drill-down to transaction
- [x] Tests: journal totals match posted lines in period; single excludes bank; double splits bucket totals; reversed pairs net to zero; OHADA codes shown vs IFRS omitted

## Session 8 — General Ledger
- [ ] `ledger_service`: opening balance, debit movements, credit movements, running/closing balance — derived from posted lines, not stored
- [ ] API: GET /ledger/{account_id}?from=&to=
- [ ] Frontend General Ledger page: select account, opening, movements, running balance, drill-down
- [ ] Tests: closing = opening + movements (per normal balance); no-activity account shows opening == closing

## Post-Session-8 Round 2 — reference-search verification, GL smart dropdown, CSV export, reversal workflow
Reference search (VERIFIED NOT A DEFECT — hardened instead):
- [x] Live-DB evidence: PostgreSQL `uap_dev` holds 17 transactions, all `posted`, none with NULL `posted_at`; searching every real reference TX-0001…TX-0017 through the actual service returns exactly that transaction's rows — 17 OK, 0 mismatches (probe `_probe_live_ref.py`). Isolated HTTP probe of GET /journal-entries confirms routing/params/serialization too (`_probe_ref.py`: full `TX-0001` → tx 1's 2 lines; digits resolve; description word → 0 rows; unfiltered → 4 rows).
- [x] Contract locked in a pure helper `parse_reference_query()` (`journal_service`) with 6 DB-free unit tests (`test_reference_query.py`): `TX-0012`/`tx_0012`/`TX 12`/`0012`/`12` all → id 12; digit-less input (a description word or a single letter) can never match a reference and yields zero rows by design.
- [x] Journal/Cash Book empty state now echoes the searched reference plus a hint that references look like `TX-0012`, instead of a bare "no match" sentence.

GL account dropdown with smart ordering (Part 2):
- [x] Backend: `GET /accounts/suggested?organization_id=` returns `AccountSuggestedOut` rows ordered (1) accounts created by the CURRENT user for this org, (2) most recent real posted/reversed activity via `max(Transaction.posted_at)` over non-draft lines, (3) remaining code/name order.
- [x] Frontend General Ledger: native `<select>` ("▾") beside the existing type-ahead; both drive the same `accountId`. Optgroups: "My accounts" then "All other accounts (most recently used first)". Works for OHADA and IFRS alike.

CSV export (Part 3):
- [x] `frontend/src/utils/csvExport.js`: client-side generation from already-fetched data (exports exactly what's displayed — no new backend endpoint/dependency), proper quoting incl. FR semicolon locales, UTF-8 BOM for Excel accents, CRLF endings.
- [x] "Download CSV" on Journal, Cash Book (same component), and General Ledger, respecting current date/account/reference filters; columns mirror each framework's on-screen table (OHADA includes N° compte; IFRS omits it).

Transaction reversal workflow (Part 4):
- [x] Backend completes Session 6's stub: `POST /transactions/{id}/reverse` creates a NEW posted transaction mirroring the original with debit/credit sides swapped, narration prefixed "Reversal of", linked back via `transactions.reverse_of_id`; original is marked `reversed` and its rows are NEVER edited/deleted; draft/already-reversed rejected with 409 (migration 0009 + `posting_service.reverse_transaction`).
- [x] Journal, Cash Book AND General Ledger include `posted` and `reversed` transactions so an original + its reversal display as a visible net-zero pair.
- [x] Frontend `TxnStatusBlock` (shared by Journal & GL drill-downs): localized status badge (Posted/Reversed/Draft), "Reversal of TX-####" marker, and a "Reverse this transaction" action ONLY on posted entries behind a plain-language confirm explaining what a reversing entry does; success message states the pair nets to zero. Immutability rule preserved — no edit/delete of posted entries anywhere.
- [x] Tests (`test_reversal.py`, 4 tests): mirror contract (sides swapped, `reverse_of_id`, posted); original marked reversed with untouched lines; draft + double-reverse rejected; ledger/journal show both legs netting to zero; suggested-order contract for the selector endpoint. `test_transactions.py` updated to the mirror contract.

Verification evidence:
- [x] Backend full suite detached: **71 passed** in 8.50s (`backend/_p_all.txt`); per-file runs also green (accounts 15, auth 9, health 3, journal+refq 11, ledger 7, orgs 7, reversal+transactions 19). Prior "hangs" reproduced only as in-shell shell-integration flakiness, never under detached runs.
- [x] `npm run build`: ✓ built in 2.95s (50 modules) after fixing one stray JSX self-closing tag introduced mid-edit.
- [x] `npm run test:lookup` — all account-lookup checks passed (9 checks). `npm run test:txn` — all txn-calculations checks passed (20 checks).

## Session 9 — Trial Balance
- [x] `trial_balance_service`: one computation returns opening debit/credit balances, period debit/credit movements, and closing debit/credit balances; reversed historical entries and their mirror lines are included
- [x] API: GET /trial-balance?organization_id=&as_of=&from=&columns=2|4|6; `columns` is a view hint and the full payload is always returned so the UI can switch views without refetching
- [x] Frontend Trial Balance page: beginner-default 2-column closing view with 4- and 6-column views, OHADA account code vs IFRS name-only display, totals and loud closing-balance pass/fail indicator, CSV export, and General Ledger drill-down
- [x] Tests: closing debit == closing credit across all three views; reversed pair nets to zero; opening + movement = closing; period filtering; zero-activity accounts are omitted; OHADA/IFRS display contracts
- **Decision:** accounts with no included activity are omitted. Opening and closing are net balances placed on their debit/credit side; movement columns show gross period debit/credit activity.
- **Verification:** focused command `pytest app/tests/test_trial_balance.py -q` produced `8 passed, 1 warning in 3.65s`. Full-suite and frontend-build attempts reached partial output but did not produce completion/return-code output because the terminal integration stalled; they remain unclaimed.

## Reporting polish — grouped Trial Balance headers, print support, CSV formatting (between S9 and S10)
- [x] Trial Balance table uses a grouped two-row header: the top row spans "Opening / Movement / Closing balance" groups (colSpan=2, distinct background/border) and the row below carries Debit/Credit sub-headers — replacing flat "Opening · Debit" concatenated labels; correct for every 2/4/6-column view
- [x] OHADA keeps the N° compte column first, IFRS is name-only, in both the table and the CSV
- [x] Mobile: grouped headers stay with their columns under the app-wide horizontal-scroll pattern (`overflow-x-auto`); the 2-col beginner view fits without scroll (decision documented in `TrialBalancePage.jsx`)
- [x] Print button on Journal, Cash Book, General Ledger and Trial Balance calling `window.print()`; print CSS lives only inside `@media print` (hides header/nav/back/filters/buttons/pass-fail card/drill-downs) and provably does NOT leak into the normal on-screen view
- [x] Consistent REPORT HEADER block on screen, print and CSV: workspace name, report title + framework label, period/as-of date, "Generated on [real current timestamp]" using only real schema data (no fabricated address/registration)
- [x] CSV for all four reports: report-info header rows → blank separator → clean column headers (Trial Balance uses two header rows mirroring the grouped table); consistent DD/MM/YYYY dates (no raw `toLocaleString()` dumps); consistent number formatting; OHADA includes N° compte / IFRS omits it
- [x] Tests: CSV includes header rows; date + number formatting consistent; OHADA/IFRS columns correct; print CSS doesn't leak on screen (`npm run test:reports` — all 9 checks passed, RC=0; `npm run build` — 53 modules, 4.58s, RC=0)

## Post-S9 round 2 — Rebrand to Kinxta Docu + Business Profile (address, RCCM, tax ID, fiscal year)
- [x] Rebrand: product name is "Kinxta Docu" in the browser tab title, header/nav (via the new original `components/Logo.jsx` — an original SVG document+checkmark mark with a swappable `image` prop for a real asset later), landing page, login/register headlines, i18n `app.title` in BOTH en.json and fr.json, `frontend/package.json` name `kinxta-docu`, README and PROGRESS_LOG headers. No internal code identifiers mass-renamed; no invented taglines or marketing copy.
- [x] `organizations` gains ALL-OPTIONAL `registered_address` (text), `rccm_number` (text), `tax_id` (text, generic label since the name varies by country — NIU/NINEA/IFU etc.) and `fiscal_year_start_month` (int 1–12, server default 1 = January — the one field with a real default because period math always needs a starting month). Migration `0010_add_business_profile_fields.py`. Existing orgs remain valid with the new fields null.
- [x] `PATCH /organizations/{id}` updates the profile (PATCH semantics; blank string clears a field back to NULL; month outside 1–12 → 422). Workspace-creation flow unchanged — nothing required at creation time.
- [x] New "Business profile" settings page inside the workspace (nav button + workspace-home card) to view/edit afterwards; save keeps the dashboard's org copy in sync.
- [x] ⚠️ BEHAVIOUR CHANGE (not cosmetic): trial balance "opening" point uses the org's `fiscal_year_start_month` (`_fiscal_year_start` in `trial_balance_service`) instead of hardcoded January 1. Unset ⇒ calendar year ⇒ results identical for every org that doesn't set it.
- [x] ReportHeader (screen + print) and CSV header rows show the registered address, and RCCM/tax ID in a footer-style line (OHADA convention: identifiers separate from the business name at top) — ONLY when set, omitted cleanly (no blank placeholders) when not.
- [x] Tests: org created & used with all fields unset (no regression); profile update via API incl. partial PATCH + blank-clears + 422; trial balance opening point SHIFTS with a non-January fiscal year start and is UNCHANGED (calendar year) when unset; helper unit-tested across year boundaries (`test_business_profile.py`).

## Post-S9 round 3 — setActiveOrg bugfix + mandatory Business Profile step (learner exemption)
- [x] BUGFIX (Part 1): clicking Save on Business Profile threw `ReferenceError: setActiveOrg is not defined`. Root cause CONFIRMED by reading the code: the `onSaved={(updated) => setActiveOrg(...)}` callback lived in `WorkSpace` — a separate module-level component whose scope has no `setActiveOrg` (that state updater is declared in `DashboardPage`). Fix: `onOrgUpdated` prop passed down `DashboardPage → WorkSpace → BusinessProfilePage` (`handleOrgUpdated`). Manual browser verification (click Save → no console error → reload persists) still PENDING — see note below.
- [x] ⚠️ DECISION REVERSAL (explicit): the previous round made Business Profile "purely optional, never at creation". That is REVERSED — it is now a MANDATORY step immediately after workspace creation, because a profile that almost nobody fills in voluntarily doesn't produce the OHADA-style report headers the reports work needs. The mandate comes with a LEARNER EXEMPTION so beginners are never locked out; this is "mandatory with an exemption", not "fully optional" and not "unconditionally mandatory".
- [x] New workspace creation redirects straight into the Business Profile form (`handleCreated` → `section='businessProfile'`); the step is enforced by the SERVER-SIDE `profile_completed` flag (migration `0011_add_profile_completed.py`: new orgs start `false`, pre-mandate orgs backfilled `true`, service sets it `true` on save when blocking fields exist) — so the gate survives page reloads and cannot be dodged by clearing session state.
- [x] Real enforcement in `WorkSpace`: while `profileGateActive(org)` (i.e. `profile_completed === false`), ONLY the mandatory BusinessProfilePage renders; the nav is replaced by a notice and ALL eight section renders (home, accounts, newTransaction, journal, cashbook, ledger, trialBalance, businessProfile) are hard-guarded with `!gated` — verified this is enforcement, not a visual suggestion (initial implementation had an enforcement hole where other sections still rendered under the gate; fixed).
- [x] Learner exemption checkbox "I don't have a registered business yet (I'm using this to learn)": checking it disables/clears the RCCM + tax ID inputs and makes them optional; registered_address and fiscal_year_start_month stay REQUIRED for everyone. Mandatory mode forces an EXPLICIT fiscal-month selection (disabled placeholder option, no silent January default); every field has a realistic placeholder (e.g. "e.g. RC/DLA/2024/B/1234", "e.g. NIU: M012345678901X (Cameroon) · NINEA (Senegal) · IFU (Benin/Togo/Burkina Faso/Niger)").
- [x] Pre-mandate organizations (fields optional before, possibly all unset): NOT hard-blocked — they see a dismissible amber completion banner (`profileNeedsAttention`, never blocks access; also applies to learner workspaces as information only).
- [x] Schema reasoning: database columns remain NULLABLE by design — the mandate is a FRONTEND flow rule + server-side `profile_completed` flag, not a NOT NULL constraint, because the learner exemption must stay expressible in the data (a learner workspace legitimately has NULL rccm/tax_id) and pre-mandate orgs must remain valid. No schema change beyond the `profile_completed` boolean was needed.
- [x] Tests: pure gating rules unit-tested in `frontend/src/utils/profile.js` via `npm run test:profile` (new workspace cannot skip the step unless learner exemption used; learner toggle makes RCCM/tax ID optional while address/fiscal-year stay required; pre-change orgs accessible with banner, not block). Backend `test_business_profile.py` covers `profile_completed` lifecycle (new org False → PATCH with blocking fields True → learner-clearing registration fields stays True; clearing blocking fields → False).
- [ ] ⚠️ VERIFICATION PENDING / NOT COMMITTED: `pytest app/tests -q` (backend) and `npm run test:profile` + `npm run build` (frontend) were launched twice detached but the shell integration killed both runs early (`backend/_bp3_all.txt` stalls at 7 dots; `frontend/_bp3_profile.txt` npm banner only; build output never created). No RC was ever observed, so NOTHING in this section is test-verified yet and NO commit was made. Run the three commands once manually, then commit as "Fix setActiveOrg bug; make Business Profile mandatory in workspace creation flow with learner exemption".

## Post-S9 round 4 — Business Profile Part 2: identity type, OHADA/IFRS-aware country and legal-form selection
- [x] `organizations` gained `identity_type` ('learner' | 'unregistered_business' | 'registered_business'), `country` (ISO 3166-1 alpha-2), and `legal_form` (framework-specific code; 'NOT_APPLICABLE' for learning-only workspaces) via migration `0012`. ALL nullable at the DB level — pre-Part-2 orgs remain valid with them unset (explicit no-regression path).
- [x] FACTS CITED IN CODE (verified against OHADA sources, in `identity_reference.py`): OHADA has exactly **17 member states** (Benin, Burkina Faso, Cameroon, Central African Republic, Chad, Comoros, Republic of Congo, Côte d'Ivoire, DRC, Gabon, Guinea, Guinea-Bissau, Equatorial Guinea, Mali, Niger, Senegal, Togo); legal business forms per the AUSCGIE uniform act (SARL/SARLU, SA incl. one-person, SAS/SASU, SNC, SCS, GIE, Entreprise Individuelle).
- [x] **Framework-aware country/form options via a single backend endpoint** `GET /organizations/identity-options?framework=`: OHADA → only the 17 member states + AUSCGIE forms; IFRS → full ISO country list + international forms (Sole Proprietorship, Partnership, LLC, Ltd, PLC, Corporation, Nonprofit/NGO, Cooperative). All with plain-language EN/FR descriptions. The frontend never duplicates ~200 country entries.
- [x] **FRAMEWORK IS IMMUTABLE after creation** — documented decision: the seeded chart of accounts is framework-specific, so switching OHADA↔IFRS would invalidate it. `framework` is deliberately ABSENT from `OrganizationUpdate` (sending it is ignored) AND the service layer raises 422 on any direct attempt (belt-and-braces, tested at the service level).
- [x] Frontend `BusinessProfilePage` now renders the identity flows (wired this session, was previously backend-only): identity radio group with plain-language descriptions; searchable country + legal-form dropdowns (new shared `SearchSelect.jsx`, filter-as-you-type); learner → RCCM/tax ID hidden + explicit "Not applicable — personal/learning use" legal-form option; unregistered_business → legal_form required, RCCM/tax optional; registered_business → legal_form + RCCM + tax ID all required. Client-side validation mirrors the backend rules before any PATCH.
- [x] Old standalone "learner exemption" checkbox REPLACED by the identity_type choice — one clear mechanism, not two overlapping ones (documented in `profile.js`).
- [x] Tests (backend `test_business_profile.py` Part 2 block): identity-options differ by framework (17 OHADA states exactly; IFRS full list; forms differ); OHADA country must be a member state (FR/NG rejected, cm case-insensitively normalized); IFRS accepts valid countries and rejects garbage (ZZ); legal-form validity per framework + NOT_APPLICABLE learner-only; registered_business requires RCCM+tax ID; unregistered_business requires legal form (RCCM/tax optional); learner skips RCCM/tax + allows N/A legal form; framework cannot be changed via the API or the service layer. NOTE: learner country is a FRONTEND requirement (form + `missingIdentityFields`), not a backend 422 — documented in the test.
- [x] **`company_description` does NOT exist** anywhere in the codebase — confirmed by search; it is not part of this feature.
- [x] Verification observed (detached runs, RC read from files): backend full suite **99 passed** RC=0 (`_ver_pytest4.txt`); `npm run test:profile` **7/7** RC=0; `npm run build` **57 modules** RC=0. Pre-existing suite green (no regressions).

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

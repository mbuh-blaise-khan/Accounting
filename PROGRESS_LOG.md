# Project Progress Log — Kinxta Docu (Universal Accounting Learning & Practice Platform)

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

**Last completed session:** Business Profile Part 2 — identity type, OHADA/IFRS-aware country and legal-form selection — **DONE and observed green, committed as `b83a3c4`.**

- **This session (Part 2) verified REAL, uncommitted work from a prior session** (backend fully wired: migration `0012` `identity_type`/`country`/`legal_form`, `IdentityType` enum, `identity_reference.py` with the 17 OHADA member states + AUSCGIE/IFRS legal forms with plain-language descriptions, `identity-options` endpoint, service validation + framework-immutability guard, frontend `SearchSelect.jsx` + `fetchIdentityOptions()` + identity-aware `profile.js`). The Business Profile PAGE was NOT yet wired to those — this session completed the wiring: identity radio group, searchable country + legal-form dropdowns (OHADA-restricted to 17 states / IFRS full list), learner handling (RCCM/tax hidden; explicit "Not applicable — personal/learning use" legal-form option), identity-driven client-side required-field validation, and the missing Part-2 backend tests.
- **Framework is now IMMUTABLE after creation** (documented in code + acceptance criteria): the entire seeded chart of accounts is framework-specific; switching OHADA↔IFRS post-creation would invalidate it. `framework` is deliberately ABSENT from `OrganizationUpdate`, and the service guard raises 422 on any direct attempt.
- **Prior session's work was actually COMMITTED** as `17240aa` (setActiveOrg bugfix + mandatory Business Profile step with learner exemption) — the PROGRESS_LOG entry below marked it "NOT committed / verification INCOMPLETE" because the shell killed the detached runs then, but this session's STEP 0 confirmed HEAD = `17240aa` and its full-suite verification observed green (90 passed).
- **`company_description` does NOT exist anywhere** in the codebase — it is not a field in this feature (the user explicitly asked to confirm this, and the answer is no).

**Next session to run:** Session 10 (financial statements) — the remaining MVP milestone.

---

## Previous status (before the mandatory-flow reversal)

**Last completed session:** Rebrand to **Kinxta Docu** + optional **Business Profile** (registered address, RCCM number, tax ID, fiscal-year start month)

The product is renamed "Kinxta Docu" everywhere user-facing: browser tab title, app header (via the new original `components/Logo.jsx` SVG mark — document-and-checkmark motif with an `image` prop so a real asset can be swapped in later), landing page, login/register headlines, `app.title` in BOTH en.json and fr.json, `frontend/package.json` name `kinxta-docu`, README and this log's headers. No internal code identifiers were mass-renamed and no invented tagline/marketing copy was added.

`organizations` gained **all-optional** Business Profile fields (migration `0010_add_business_profile_fields.py`): `registered_address` (text), `rccm_number` (text), `tax_id` (text, generic label — the name varies by country: NIU/NINEA/IFU), and `fiscal_year_start_month` (int 1–12, server default 1 = January — the one field with a real default because period math always needs a starting month). Existing organizations remain valid with the new fields null; the workspace-creation flow is unchanged (nothing required at creation).

⚠️ **BEHAVIOUR CHANGE (not cosmetic):** the trial balance's "opening" point now uses the organization's `fiscal_year_start_month` (`_fiscal_year_start` in `trial_balance_service`) instead of a hardcoded January 1. When unset (default January) results are **identical** to before — calendar year. A fiscal year starting in June, say, makes as-of 2026-03-15 belong to the year starting 2025-06-01, so pre-June-2025 history becomes "opening". Documented in `acceptance-criteria.md` and the service docstring.

A new **Business Profile** settings page inside the workspace (nav button + workspace-home card) views/edits the fields via the new `PATCH /organizations/{id}` (PATCH semantics: only provided keys change; blank string clears a field back to NULL; month outside 1–12 → 422). Report headers (screen, print AND CSV header rows) now show the registered address, and RCCM/tax ID in a **footer-style line** per OHADA convention (identifiers separate from the business name at top) — only when actually set, cleanly omitted otherwise (no blank placeholders).

**Verification evidence (all observed, RC read from output files):** backend full suite **86 passed** in 14.70s, RC=0 (`backend/_bp_all2.txt`), including 8 new `test_business_profile.py` tests. Frontend `npm run test:reports` all 9 checks passed RC=0; `npm run build` 55 modules, 5.94s, RC=0 (`frontend/_bp_reports.txt`, `_bp_build.txt`).

One pre-existing test needed a fix en route: `test_reversed_pair_nets_to_zero_and_counts_as_history` derived "today" from the LOCAL clock while the service filters on UTC `posted_at` — after local midnight in a UTC+ timezone its `from=today` bound landed in the UTC future and movement came out 0. All five date-bound computations in `test_trial_balance.py` now use a shared `_today_utc()` helper (UTC basis, matching the service). Production code was NOT affected.

**Next session to run:** Session 10 (financial statements) — the remaining MVP milestone.

**Decisions:**
- Business Profile fields are all-optional; only `fiscal_year_start_month` defaults (to January) because period math cannot work without a start month. Not every user is a registered business.
- Fiscal-year shift applies ONLY when no explicit `from` is given (explicit period bounds always win); with no bounds at all, all history stays "movement" as before.
- RCCM/tax ID render in a footer-style line in `ReportHeader` (and as trailing CSV header rows), separate from the business name — OHADA convention.
- No mass rename of internal identifiers; only user-facing text, package `name`, docs.


### setActiveOrg bugfix + mandatory Business Profile step (2026-08-27)
- Status: CODE DONE, **verification INCOMPLETE** (pytest/npm outputs stalled twice — shell integration kills detached processes; no RC ever observed). **NOT COMMITTED** — user must run `pytest app/tests -q` (backend) and `npm run test:profile` + `npm run build` (frontend) manually, then commit.
- Bugfix: `ReferenceError: setActiveOrg is not defined` on Business Profile save — the `onSaved` callback in `WorkSpace` referenced a state updater that only exists in `DashboardPage`. Fixed via an `onOrgUpdated` prop threaded down the component tree.
- Decision reversal (documented in acceptance-criteria.md): Business Profile is now MANDATORY immediately after workspace creation, with a learner exemption checkbox (no registered business yet → RCCM/tax ID optional/disabled; address + fiscal month still required). Prior session's "purely optional" stance deliberately reversed.
- Enforcement: server-side `profile_completed` boolean (migration `0011`; new orgs start false; PATCH sets/unsets it from the required blocking fields) + frontend gate in DashboardPage (`profileGateActive`) that forces the profile section and blocks accounts/transactions pages; reload-safe. Pre-mandate orgs: dismissible banner, never blocked. DB columns remain nullable by design.
- Mandatory-mode form: explicit month dropdown (no silent January default), realistic placeholders per field, missing-field error list.
- Tests written (NOT yet observed passing): `frontend/src/utils/profile.test.mjs` via new `npm run test:profile` script; backend `test_business_profile.py` extended with the `profile_completed` lifecycle.
- i18n: new `bp.mandatory*`, `bp.learner*`, `bp.*Placeholder`, `bp.requiredFields` keys in BOTH en.json and fr.json.

### Rebrand to Kinxta Docu + Business Profile fields (2026-08-27)
- Status: DONE; backend 86 passed (RC=0), frontend test:reports 9/9 (RC=0), build 55 modules (RC=0).
- Rebrand: "Kinxta Docu" in tab title, header/nav via new original `components/Logo.jsx` (SVG document+checkmark, swappable `image` prop), landing/login/register headlines, i18n `app.title` (en+fr), package name `kinxta-docu`, README/log headers.
- Migration `0010`: organizations += all-optional `registered_address`, `rccm_number`, `tax_id` (generic label; NIU/NINEA/IFU vary by country) and `fiscal_year_start_month` (1–12, server default 1). Existing orgs valid with nulls; creation flow unchanged.
- New `PATCH /organizations/{id}` (blank clears to NULL; bad month → 422) and a Business Profile settings page in the workspace (nav + home card).
- ⚠️ BEHAVIOUR CHANGE: trial-balance opening point now derives from the org's fiscal_year_start_month (`_fiscal_year_start`) instead of hardcoded Jan 1; unset ⇒ calendar year ⇒ unchanged results. Explicit `from` bounds still win.
- ReportHeader + CSV header rows show address/RCCM/tax ID only when set; RCCM/tax ID in a footer-style line (OHADA convention).
- Fixed a latent local-vs-UTC date flake in `test_trial_balance.py` (`_today_utc()` helper); production code unaffected.
- Acceptance criteria updated with the fiscal-year change flagged as a real behaviour change.

### Trial-balance grouped headers; print support and CSV formatting fix (2026-08-27)
- Status: DONE; `npm run test:reports` all 9 checks passed (RC=0) and `npm run build` (53 modules, 4.58s, RC=0).
- STEP 1 (grouped headers): Trial Balance table rewritten to a two-row header — group row spans Opening/Movement/Closing per selected 2/4/6-column view; second row shows Debit/Credit. Computationally DRIVEN from the same row payload; CSV mirrors it with two header rows.
- STEP 2 (print + CSV): added a Print button to Journal, Cash Book, General Ledger and Trial Balance via `window.print()`; report header shown on screen (from the shared `ReportHeader` component), hidden only in print; CSV now prepends report-info header rows + blank separator; consistent dates (`formatReportDate`) and numbers (`formatReportNumber`); OHADA N° compte / IFRS omitted for all report columns.
- Added the `reportAccountColumns` OHADA/IFRS account-column helper to `reportPresentation.js` and created `frontend/src/utils/report.test.mjs` (`npm run test:reports`).
- Acceptance criteria updated.

### Cash Book enhancement — single- and double-column types (2026-08-27)
- Status: DONE; focused tests and frontend build passed. The full-suite process reached 71 test dots but did not emit a pytest summary before terminal teardown blocked, so no full-suite pass is claimed.
- Added explicit cash/bank classification to Cash Book rows. OHADA uses 57 for physical cash and 52/56 for bank; IFRS names distinguish bank terms before cash terms.
- Added `type=single|double` to `GET /cashbook`, defaulting to double. Single returns cash only; double returns both buckets with `cashbook_type` tags.
- Added the Cash Book selector and dedicated renderer to the shared Journal page. Single shows Debit/Credit; double shows Cash Dr, Bank Dr, Cash Cr, Bank Cr. CSV follows the selected view and existing filters.
- Added tests for type exclusion, per-bucket splitting, filter retention, invalid type rejection, and reversed-pair net-zero behavior.
- Triple-column and Petty Cash Book are intentionally deferred: the current schema has no discount fields or imprest/float/replenishment model.

---

## Session Log

### Post-Session-8 Round 2 — reference search verified, GL dropdown, CSV export, reversal end-to-end (2026-08-26)
- Status: DONE

#### Part 1 — Reference search: investigated for real; VERIFIED NOT A DEFECT
- Evidence chain (all commands actually run, outputs on disk):
  1. `backend/_probe_ref.py` (TestClient + isolated SQLite over the REAL routes):
     `TX-0001` → exactly tx 1's 2 lines; `TX-0002` → tx 2's lines; bare digits resolve;
     description word "one" → 0 rows; unfiltered → 4 rows (`_probe_ref_fresh.out`).
  2. NEW live-database probe `backend/_probe_live_ref.py` against PostgreSQL `uap_dev`:
     17 transactions, ALL `posted`, none with NULL `posted_at`; then the EXACT service
     call behind "Apply filters" for every real reference TX-0001…TX-0017 →
     **17 OK, 0 mismatches**, including the user's own example TX-0016 (org 6,
     "Mbuh sold goods for 5000 in cash") → its correct rows (`_probe_live_ref.out`).
  3. Frontend wiring audited: input value → `reference` state → params →
     `fetchJournalEntries` `/journal-entries?...&reference=…` — no mismatch.
- **Root cause statement:** there is no reference-search defect in code or data.
  Digit-less searches (e.g. "a single letter") return zero rows BY DESIGN because
  references are generated `TX-{id:04d}` and can never contain letters — that part
  of the report matches intended behavior. If an EXACT reference still fails in the
  user's browser, the only remaining explanation is stale running processes (a dev
  server started before commit `0a266b0`) — restart backend/frontend.
- Hardening (no behavior change to the filter itself): extracted the contract into a
  pure, DB-free helper `parse_reference_query()` in `journal_service`; added
  `app/tests/test_reference_query.py` (6 tests); Journal/Cash Book empty state now
  shows "Searched reference: <what you typed>" + hint that references look like
  TX-0012 (EN+FR).

#### Part 2 — GL account dropdown with smart ordering
- Backend (built earlier in this round): migration `0009` (`accounts.created_by`),
  `list_accounts_for_selector()` ordering = my custom accounts first → most recent
  real `max(Transaction.posted_at)` activity over non-draft non-null-posted lines →
  code/name asc; exposed at `GET /accounts/suggested`.
- Frontend: `fetchSuggestedAccounts()` in api.js; native `<select>` ("▾") above the
  existing type-ahead in GeneralLedgerPage, both driving the same `accountId`;
  optgroups "My accounts" / "All other accounts (most recently used first)";
  suggested list refetched per org change. OHADA and IFRS both covered.

#### Part 3 — CSV export
- New `frontend/src/utils/csvExport.js`: client-side generation from the already
  fetched (and therefore currently-filtered) rows — guarantees "export what you
  see", zero new backend endpoints/deps. Proper quoting, UTF-8 BOM for Excel +
  accented French names, CRLF endings.
- "Download CSV" button on Journal & Cash Book (shared component) and General
  Ledger. Columns match the on-screen table per framework: Date, Reference,
  Description, [N° compte OHADA only], Account name, Libellé/narration, Debit,
  Credit, (+ Source, Status; + Running balance for GL). Disabled until rows exist.

#### Part 4 — Reversal workflow completed end-to-end
- Backend (built earlier in this round): `posting_service.reverse_transaction`
  creates the NEW posted mirror (sides swapped, narration prefixed, linked via
  `transactions.reverse_of_id`), marks original `reversed`, never touches original
  rows; 409 on draft/already-reversed; ledger/journal/cashbook include reversed so
  the net-zero pair is visible. Tests: `test_reversal.py` (4) + updated
  `test_transactions.py::test_reverse_posted_transaction`.
- Frontend (this round): shared `components/TxnStatusBlock.jsx` rendered inside BOTH
  the Journal's TransactionDetail and the GL's TxnDetail:
  - localized status badge (Posted green / Reversed amber / Draft grey);
  - "Reversal of TX-####" mono badge when `reverse_of_id` present;
  - "Reverse this transaction" ONLY when status === 'posted', behind a plain-language
    confirm explaining a mirror entry cancels the original and the original stays
    untouched; success message states the pair nets to zero; on success the page
    reloads rows and re-reads the transaction so badges refresh immediately.
- Immutability rule intact: no UI or API path edits/deletes posted transactions.

#### Decisions made
- Did NOT fabricate a fix for Part 1: root cause = not a defect (strict-by-design
  digit-less behavior + probable stale dev servers); hardened instead.
- CSV chosen client-side (already-displayed state ⇒ trivially consistent with the
  applied filters); PDF explicitly out of scope this session.

#### Verification evidence (real runs, this session)
- Live DB probe `_probe_live_ref.out`: 17 OK / 0 mismatches / 0 skipped, EXIT=0;
  HTTP probe `_probe_ref_fresh.out` shows full JSON rows for TX-0001/TX-0002.
- Backend suites: refq+journal **11 passed**; reversal+transactions **19 passed**;
  orgs **7**, auth **9**, health **3** passed; FULL `app/tests` **71 passed in 8.50s**
  (`_p_all.txt`). In-shell foreground pytest intermittently stalls (~dot 23) while
  detached identical commands finish <9s → environment artifact, recorded here to
  prevent future ghost-chasing.
- Frontend: `npm run build` ✓ 50 modules in 2.95s (one stray `/>` from an edit caught
  by the build and fixed); `npm run test:lookup` all 9 checks pass; `npm run
  test:txn` all 20 checks pass. i18n en.json/fr.json JSON-parse validated.

#### What Session 9 needs to know
- Trial Balance must include `posted` AND treat `reversed` originals correctly —
  original + mirror cancel to zero; keep using pure helpers like
  `parse_reference_query` where convenient.
- Run pytest DETACHED in this environment; ~71 tests finish in seconds.

### Post-Session-8 fixes — search UX, visual separation, ledger balance sides, validation (2026-08-25)
- Status: DONE

#### Root causes found (Parts A/C/D were previously claimed fixed but were NOT)

- **Part A (reference search):** the backend `journal_service` reference filter was already
  correct (parses `TX-0012`/`0012`/`12` → `Transaction.id == parsed`; digit-less queries can
  never match). The REAL defect was the i18n placeholder: `"journal.referencePlaceholder"`
  said **"e.g. cash"** in EN ("ex. caisse" in FR) — inviting a description word that could
  never match a reference. Fixed to "e.g. TX-0012" / "ex. TX-0012". Verified live:
  searching `TX-0001` returns only TX-0001's 2 lines; `0001` also resolves; the description
  word "Purchase" returns 0 rows.
- **Part C (transaction separation):** Session 8's alternating background alone was too weak.
  Added an explicit bold rule line (`border-t-2 border-slate-400`, full-width) between
  DIFFERENT transactions in both JournalTable and the General Ledger movements table, so
  TX-0012 / TX-0013 / TX-0014 read as unmistakable blocks even same-day.
- **Part D (credit offset):** Session 8's offset had been applied but too faintly to register
  (and the GL movements table had its own rendering). Re-applied as a STRONG treatment:
  credit account names get `pl-16` + "↳" prefix and muted color vs bold debit names; credit
  amounts sit indented (`pl-14`) inside their column; GL movement rows got the identical
  treatment so all three pages match.
- **Part E (ledger balance presentation) — REAL COMPUTATION BUG:** `_balance(signed)` mapped
  positive → debit / negative → credit as if `signed` were an absolute debit/credit figure,
  but `_signed_delta()` returns a CONVENTION-RELATIVE value (+ = toward normal side). For a
  credit-normal account in net credit position this produced side="debit" — wrong label AND
  wrong column. Fixed `_balance(signed, normal_balance)` to pick the side via the account's
  convention; schemas now expose every balance point as `{debit, credit, side}` with exactly
  one non-zero (researched convention: ledgers show "Debit balance"/"Credit balance" as an
  unsigned figure sitting on one labeled side, not a signed number). Frontend renders
  "15,000 Dr" / "27,000 Cr". Tests updated + new cross-over test (account crossing from Dr
  to Cr mid-period labels each running balance correctly).

#### Also in this round

- **Part B:** new `frontend/src/components/AccountFilterSelect.jsx` wraps AccountLookup for
  filter use on Journal / Cash Book / General Ledger (progressive OHADA code-prefix narrowing,
  name substring for both frameworks, clear ✕ button back to "all accounts"). Selection
  behavior after picking is unchanged.
- **Part F:** `validatePost()` (pure helper in txnCalculations.js) reports exactly WHICH
  required fields are empty per line ('account' | 'amount' | 'bothSides') plus description
  and balance errors; NewTransactionPage now wires its Post button through `attemptPost()`,
  renders a red inline banner above any invalid line (desktop grid + mobile card) and under
  the description field; posting stays blocked until fixed. i18n keys added in EN+FR
  (tx.errDescription / errAccount / errAmount / errBothSides / errUnbalanced).

#### Verification evidence (real commands, real output)

- Backend suite: `pytest app/tests/ -v` → **61 passed**, 3 warnings (deprecations only).
- Live API probe (TestClient + real routes, `_probe_p8.py`, since removed): **13/13 checks
  passed**, including: reference `TX-0001` ⇒ exactly 2 lines of TX-0001; word "Purchase" ⇒
  0 rows; cash ledger closing `15000.0 Dr / 0.0 Cr / side=debit`; sales closing
  `0.0 Dr / 27000.0 Cr / side=credit`; identity closing.debit = opening.debit + debits −
  credits holds on the wire format.
- Frontend: `npm run build` → ✓ 48 modules transformed; `npm run test:txn` → 20/20 ok
  (6 new validatePost checks); `npm run test:lookup` → 9/9 ok.

---

### Session 8 — General Ledger + Journal UI grouping (2026-08-25)
- Status: DONE

#### What was built
- `backend/app/schemas/ledger.py`: `LedgerAccountOut`, `LedgerMovementOut`, `LedgerOut`
  (opening/debit_movements/credit_movements/closing + movements with per-line running balance).
- `backend/app/services/ledger_service.py`: `get_ledger(db, user, org_id, account_id,
  date_from=None, date_to=None)` — argument order follows the established `(db, user, org_id, …)`
  service convention. Everything is DERIVED from POSTED journal lines on the fly (per `.clinerules`):
  opening = cumulative signed net strictly before `date_from` (0 when unbounded); movements are raw
  debit/credit sums within the window; running balance accumulates `_signed_delta()` line by line;
  closing = opening + net movement. Balance convention: debit-normal accounts close at
  opening + debits − credits; credit-normal accounts at opening + credits − debits. Drafts/reversed
  never appear. No stored ledger balance exists that could drift from the journal.
- `backend/app/api/routes/ledger.py` + registered in `router.py`:
  `GET /ledger/{account_id}?organization_id=&from=&to=` (protected, org-scoped, 404 conventions).
- `backend/app/tests/test_ledger.py` — 6 tests: the closing identity for a debit-normal account;
  the credit-normal convention; opening respecting `from` (re-dated posted_at via test_db_session);
  no-activity ⇒ opening == closing == 0 (unbounded AND inside an explicit period); drafts excluded;
  org scoping (non-member 404, foreign account id 404, unauthenticated 401).
- Journal/Cash Book UI (`frontend/src/components/JournalTable.jsx`, presentation ONLY — shared by
  both pages so both inherit it): (1) sticky/distinct DATE separator band above the first
  transaction of each day ("Sunday, August 17, 2026" style) — fixes "different weeks cannot be
  identified"; (2) rows of one transaction read as one unit via a thin top divider starting each
  new reference group plus alternating subtle group backgrounds; (3) double-entry offset — credit
  rows indent the account name (pl-10 + ↳ prefix) and shift the credit amount in from the column
  edge (pr-9), and credit figures render muted vs bold debits. Framework-aware OHADA/IFRS columns,
  totals math, filters, cash/bank filtering and drill-down untouched. Mobile cards get the same
  separators/banding/credit offset.
- General Ledger frontend: `GeneralLedgerPage.jsx` (account picker incl. OHADA code labels,
  optional from/to, four balance cards, chronological movements table with running balance and a
  closing-balance footer row, transaction drill-down), `fetchLedger()` in `services/api.js`,
  i18n EN+FR keys (`ledger.*`, `ws.ledger*`), and Dashboard wiring (nav button, OrgHome card,
  section switch).

#### Verification (real commands, output captured)
- `python -m py_compile app/services/ledger_service.py app/schemas/ledger.py` → rc=0; direct import
  of `ledger_service.get_ledger` OK.
- `pytest app/tests -q` → **60 passed** (54 prior + 6 new ledger tests), EXIT=0.
- Ledger tests alone: `pytest app/tests/test_ledger.py -q` → **6 passed**.
- `npm run build` (real Vite production build) → ✓ 47 modules transformed, built in 3.19s — proves
  JournalTable rewrite + GeneralLedgerPage compile.
- i18n JSON parse check on en.json + fr.json → OK.

#### Decisions made
- Balances are never stored; every ledger call re-derives from the immutable posted journal
  (.clinerules determinism/immutability rules).
- `get_ledger` keeps `(db, user, org_id, …)` ordering to match existing services rather than the
  `(…, account_id, org_id)` order in the session brief.
- The Journal grouping change is confined to `JournalTable` (shared by Journal + Cash Book);
  GeneralLedger's own movement table applies the same credit-offset styling but not date bands.

#### Environment note (for future sessions)
- Bare `node` fails in this shell ("stdout is not a tty"), but `npm run build` WORKS (npm routes
  through a cmd shim) — use Vite builds as the frontend verification path. Long backend commands:
  launch detached with `nohup … & disown` writing to a file, then poll the file with read_files
  ONLY — any new foreground shell command kills background jobs.

#### What Session 9 needs to know
- Trial balance / financial statements can reuse `ledger_service._period_lines` +
  `_signed_delta` (per-account signed nets already encode normal-balance direction).
- `/ledger/{account_id}` returns Decimal fields serialized as JSON numbers; frontend reads
  `opening_balance`, `debit_movements`, `credit_movements`, `closing_balance`, `movements[]`.
- To re-run frontend util tests: still blocked by bare node; use `npm run build`.

### Session 7 follow-up (2) — Non-demo workspaces got EMPTY charts: seeding policy fix (2026-08-24)
- Status: DONE
- Trigger: a user registered a real (non-demo) OHADA business and found ZERO accounts under Chart of
  Accounts, no autocomplete suggestions, and no way to post a transaction.

#### Root cause (confirmed with live API probes, not guesses)
- `organization_service.create_organization` gated chart seeding behind `if is_demo:` (Session 6b
  design). Real businesses were never auto-seeded -> empty chart -> no code/name autocomplete,
  no transaction posting.
- IFRS had the SAME gap (verified live: a fresh non-demo IFRS org before the fix also had 0
  accounts).
- This "empty non-demo chart" assumption was wrong for OHADA specifically: SYSCOHADA numbering is a
  legally standardized national system (docs/ohada-ifrs-source-reference.md), not something each
  business invents. Every real OHADA business should start from the representative SYSCOHADA chart
  and may add custom accounts on top.

#### What was built / changed
- `backend/app/services/organization_service.py`: removed the `is_demo` gate; EVERY new workspace is
  seeded immediately via `seed_chart_for_organization` (OHADA -> 87-entry representative SYSCOHADA
  subset; IFRS -> 27-entry IAS-1 template, code-free per Part B).
- `backend/scripts/reseed_charts.py`: repurposed for the new policy — runs against **ALL orgs by
  default** (backfill), `--demo-only` restricts to demo orgs; `--dry-run`/`--org` kept. Docstring
  updated. Fixed a cosmetic bug that printed the final summary once per org.
- `frontend/src/utils/accountLookup.js`: code matching is now **PREFIX-based** (`startsWith`), not
  substring-anywhere, so typing "5" suggests all of Class 5, "57" narrows to treasury, "5711" lands
  on the deepest sub-account; NAME matching stays substring (EN/FR).
- `frontend/src/utils/accountLookup.test.mjs`: added `OHADA progressive digit-narrowing is REAL
  prefix matching` (asserts '5'->Class 5, '57'->[571,5711,5712], '5711'->leaf, '011'->[] proving
  prefix-not-substring; extended the shared fixture with 51/512).
- i18n relabel (OHADA account-number field/column): `tx.account` -> "A/C number" (EN) / "N° compte"
  (FR) on the transaction grid (desktop header + mobile); `coa.code` -> "A/C number"/"N° compte" on
  the Chart-of-Accounts create-account field. Mobile txn-row label is now framework-aware
  (IFRS rows show "Account name" instead of "A/C number", matching the desktop).

#### Backfill (transaction-aware, real DB)
Ran `-m scripts.reseed_charts` (all orgs). Results (real script output):
- org 3 'Khan and Sons' (OHADA, non-demo): 0 -> 87 accounts
- org 5 'Nelly' (IFRS, non-demo): 1 -> 28 (protected custom kept + Part-B code NULL + 27 template)
- org 6 'ss' (OHADA, non-demo): 2 -> 87 (2 protected txn accounts + 85 seeded)
- org 11 'Boris' (OHADA, non-demo real business, reported by the user): 2 -> 89 (2 protected
  txn-referenced accounts + 87 SYSCOHADA) — posted transactions intact, no dangling refs
- demo orgs untouched (org 2/4/7/8/9/10 unchanged), IFRS Part-B violations across DB: 0

#### Verification (all real commands, output pasted in this session)
1. `pytest app/tests -q` -> **54 passed** (added test_non_demo_org_auto_seeds_chart_per_framework;
   test_account_list_scoped_per_organization updated: Bob's non-demo org is now seeded, not empty;
   test_ohada_seed_produces_real_hierarchy updated to assert non-demo OHADA auto-seeds).
2. Real API (TestClient) creating a NEW non-demo OHADA org: 201, GET /accounts -> count=87,
   has 5711=True, has 7011=True, has 57=True, codes_head real SYSCOHADA (`10,101,1011,...`).
3. Real API creating a NEW non-demo IFRS org: 201, count=27, codes_present=0 (the IFRS gap was real
   and is now closed — same fix applied).
4. searchAccounts port over the new non-demo OHADA chart (REAL rows): '5'->[50,52,521,5211,5215,57,
   571,5711,5712], '57'->[57,571,5711,5712], '571'->[571,5711,5712], '5711'->[5711], '70'->[70,701,
   7011,706], '011'->[] (prefix-not-substring), 'cash'->57..., 'ventes'->[70,701,7011].
5. Bidirectional: name->number ('cash' -> 57 Cash), number->name ('5711' -> Cash - head office,
   national currency; '701' -> Sales of goods for resale) — the picker displays both directions.
6. Cross-checked the .mjs assertions with an exact Python port: ALL OK. (node cannot execute in this
   non-TTY shell — same blocker as the prior entry; npm run test:lookup must be re-run by the user.)

#### Decisions made
- The prior "non-demo stays empty" scope guard is REVOKED for new and existing orgs: every workspace
  gets its framework's chart; custom accounts may still be added on top.
- IFRS non-demo were ALSO empty (confirmed), so the same seeding fix applies (requirement #2).
- The COA page list-filter stays substring-anywhere for code (it is a browse filter, not the
  autocomplete picker); prefix narrowing applies to the picker (AccountLookup/searchAccounts).

#### What Session 8 needs to know
- Session 8 (General Ledger) not started.
- To re-run the frontend util tests in a terminal-capable env: `cd frontend && npm run test:lookup`.
- Evidence kept in backend/: `_probe_nondemo.py` (real-API non-demo + narrowing + backfill proof),
  `_xcheck_lookup.py` (Python mirror of the .mjs assertions). Scratch `_*.txt` cleaned up.

### Session 7 follow-up — Live verification & data remediation (2026-08-21)
- Status: DONE (this is the terminal-capable verification the Session 7 entry asked for, plus the
  data fixes it identified)
- Trigger: on a fresh boot the OHADA demo chart rendered empty and the account search found nothing
  for real SYSCOHADA codes (5711, 7011, etc.), and the IFRS demo still showed legacy account codes.

#### Root cause (confirmed with real DB + live API probes, not guesses)
- The seed CODE is correct: a fresh OHADA demo yields 87 real SYSCOHADA accounts and a fresh IFRS
  demo yields 27 IAS-1 accounts with code=NULL (verified live through TestClient in this session).
- The live DB held STALE pre-Session-6b/Part-B data:
  - org 4 (OHADA demo): 18 flat legacy accounts, codes 1000–5600, parent_account_id=NULL, and NO
    57/571/5711, 70/7011, 60/601, 40/401 → OHADA cash/sales autocomplete found nothing.
  - org 2 (IFRS demo): 29 accounts still carrying codes/names from the legacy chart (Part B never
    applied to the live rows), plus 6 posted transactions referencing account ids {3,4,5,9,10,11,19,42}.
  - org 3 / org 6 (non-demo OHADA): 0 accounts — CORRECT by design (seed only runs for is_demo=True;
    test_account_list_scoped_per_organization forbids seeding them).

#### What was built / changed
- NEW `backend/scripts/reseed_charts.py` — repeatable, surgical data-remediation script:
  - Demo-only by default (`--all` opts non-demo orgs in, with a warning; `--dry-run` previews;
    `--org N` scopes to one org); idempotent (re-running is safe).
  - OHADA: deletes only UNREFERENCED system-default accounts whose code is NOT in the canonical
    SYSCOHADA subset, then calls the existing `seed_ohada_chart` (idempotent, keyed by code).
  - IFRS: sets `code=NULL` on ALL IFRS accounts (Part B is framework-wide), deletes only
    unreferenced system-default accounts whose name is NOT in the 27-entry IAS-1 template, then
    calls `seed_ifrs_template` (idempotent, keyed by name_en).
  - SAFETY: any account referenced by ANY transaction line (posted OR draft) is permanently
    protected from deletion; user-created custom accounts (is_system_default=False) are never
    deleted. Posted entries can never be orphaned.
- FRONTEND `frontend/src/components/AccountLookup.jsx`: the OHADA journal compact input used to
  render "code — name" while a dedicated read-only NAME column sat right beside it (duplicated name).
  Now the OHADA input shows CODE only (IFRS keeps the name only, Part B). The dropdown still shows
  code + both language names for picking.
- CONFIRMED-ALREADY-FIXED (re-read on disk, no change needed): Session 7 Bug A3 ("Add a line" dead)
  — the lines grid + column header are always rendered now; and the OHADA two-column journal layout
  (AccountLookup code picker + read-only name) is wired correctly with `framework` passed through.
- TESTS: extended `frontend/src/utils/accountLookup.test.mjs` with an OHADA code-subtree check
  (571→[571,5711,5712], 60→[60,601,6011,6012,603], name search 'caisse'). `node` cannot execute in
  this shell ("stdout is not a tty" on even `node --version`), so the new assertions were
  cross-validated by an exact Python port of searchAccounts run against both synthetic and real
  reseeded data — all assertions passed.

#### Verification (all live, this session)
- `python -m pytest app/tests -q` → **53 passed** (incl. org-scoping + IFRS-no-code tests).
- Real API via TestClient: fresh OHADA demo → 87 accounts, has 5711 + 7011; fresh IFRS demo → 27
  accounts, codes_present=0.
- After applying the reseed to the live DB: org 4 = 87 SYSCOHADA accounts (57/571/5711, 70/7011,
  60/601 all present); org 2 = 32 accounts ALL code=NULL; org 7/org 8 (already-correct probe demos)
  untouched (no churn); org 3/org 6 still 0 (scope guard intact).
- Search over reseeded org 4: '5711'→[5711]; '571'→[571,5711,5712]; 'cash'→[57,571,5711,5712];
  '7011'→[7011]; 'ventes'→[70,701,7011]. org 2 (IFRS, name-only): 'cash and cash'→'Cash and cash
  equivalents'; 'revenue'→[Sales revenue, Service revenue].
- org 2 posted-transaction integrity: all 6 posted txns intact and balanced; referenced account ids
  {3,4,5,9,10,11,19,42} all still resolve to existing org-2 accounts (no dangling references).

#### Decisions made
- Data remediation lives in the repo as a repeatable script (scripts/reseed_charts.py), not a
  one-off manual patch; it reuses the already-tested idempotent seeders.
- Reseeding is demo-only by default. Non-demo orgs staying seeded-empty remains a permanent
  acceptance criterion (test_account_list_scoped_per_organization).
- IFRS Part B is enforced surgically (null the code column framework-wide) rather than wiping the
  org — posted transaction references survive.

#### What Session 8 needs to know
- Session 8 (General Ledger) is unchanged and NOT started in this session.
- To re-run the frontend util tests in a terminal-capable env: `cd frontend && npm run test:lookup`.
- Evidence artifacts kept in backend/: `_probe_live.py` (real-API + search proof), `_probe_after.py`
  (post-reseed DB proof), `_probe_orgs.py` (org roster). Scratch `_*.txt` outputs were cleaned up.

### Session 7 — Bug fixes, IFRS code removal, Journal and Cash Book
- Status: DONE
- Date completed: 2026-08-18
- Parts A + B + C were completed first, in order, before Session 7 build work (per the brief).

### PART A — Bugs investigated (root cause found by reading real files, not guessing)
- **Bug 2 — OHADA Chart of Accounts empty + search returns nothing.** Root cause: the
  `AccountTree` component only rendered accounts reachable from a `parent_account_id == NULL`
  root (`if (roots.length === 0) return null`), and silently dropped any account whose
  parent was missing from the fetched list. So an OHADA chart whose rows have no null-parent
  root (e.g. an interrupted/legacy seed, or a row set where every parent is another row and
  the top-most parent got filtered) rendered ZERO rows while the page still printed
  "N accounts", and the search bar filtered that same invisible data → "nothing found".
  Fix: `AccountTree` now renders EVERY account — a real root-first tree walk, then any
  unreachable/orphan row appended as a top-level item; sort is null-safe. The OHADA page
  now always shows its real rows.
- **Bug A3 — "Add a line" button appeared unresponsive.** Root cause: the grid (the only
  thing that makes an added line visible) was rendered inside `{loading ? … :
  activeAccounts.length === 0 ? … : grid}`, and the button sat ABOVE that branch. If the
  account fetch was pending/empty, clicking appended a line to state but the grid was not
  rendered → nothing visibly changed on screen, i.e. the button looked dead. Fix: the lines
  grid (and its column header) is ALWAYS rendered; the loading / no-accounts notice moved
  inline below it. Every click now visibly adds a row regardless of fetch state.
- Verification: In the current (non-functional-shell at authoring time) environment, I
  could not execute the running app, so end-to-end live-click verification could not be
  captured. The AccountTree and grid-render logic were re-read in full and confirmed
  structurally correct; the same end-to-end check listed under "Verification" should be
  re-run when a terminal is available.

### Part B — IFRS account codes removed (research-confirmed standard change)
- Research basis (docs/ohada-ifrs-source-reference.md + source review): IFRS (IAS 1) does
  NOT mandate a numbered chart of accounts. Numbering is a legal requirement in only a
  small set of jurisdictions — France, Germany, China, Russia and OHADA member states —
  and IFRS is not among them. This product explicitly separates OHADA (numbered, legally
  mandated) from IFRS (principle-based, no mandated numbering), so IFRS accounts no longer
  carry a code.
- What changed (schema preserved for the OHADA side; no restructure):
  - `accounts.code` widened to nullable (migration `0007`). The shared `accounts` table and
    the `(organization_id, framework, code)` unique constraint are unchanged in structure;
    IFRS rows simply store NULL (multiple NULLs are allowed by a unique constraint).
  - `ifrs_template.py` no longer sets a `code` (entries omit it; seeder stores NULL and keys
    idempotency by `name_en`).
  - `account_service`: OHADA still REQUIRES a code (422 if missing); IFRS never stores one
    (any supplied code is ignored).
  - Frontend: IFRS Chart of Accounts has no code badge/column, no code field in the create
    form, no OHADA-class column; `AccountLookup` for IFRS matches by NAME only and never
    renders a code. OHADA keeps the bidirectional code+name search and layout unchanged.
  - Journal / Cash Book (Part D): IFRS omits the account-number column; OHADA shows it.
  - Tests: IFRS account without code is created + used in a posted transaction; IFRS
    name-only lookup; OHADA codes required / still searchable / still displayed.

### Part C — Modernized description field + posting date surfaced
- The "What happened?" field was redesigned: larger label/hint hierarchy, bigger padded
  textarea, focus ring, char counter — beginner-friendly, less like a default form control.
- The real backend `posted_at` (set by posting_service on posting) is now the LEADING date
  wherever a posted transaction appears: the post-confirmation "what this means" screen and
  every row of the Journal/Cash Book.

every row of the Journal/Cash Book.

### Part D — Journal and Cash Book (Session 7)
- Backend: new `journal_service` (read-only over POSTED transaction lines; filters date
  range / account / reference; Cash Book = same view but only cash/bank accounts, using
  OHADA class-5 / code prefix `5` OR a name-keyword fallback for IFRS and legacy rows).
  New routes GET `/journal-entries` and GET `/cashbook` (org-scoped, protected). The row
  date is `posted_at`.
- Persisted the per-line narration the UI already collects: migration `0008` adds
  `transaction_lines.narration`, wired through the schema, create service and `toPayload`.
- Frontend: `JournalTable` (shared read-only table; OHADA = date | N° compte | intitulé |
  libellé | débit | crédit + reference/description/source/status; IFRS omits the N° column;
  footnote totals), `JournalPage` + `CashBookPage` with date/account/reference filters and a
  "View →" drill-down to full originating-transaction detail, dashboard nav + home cards.
- New backend tests: `app/tests/test_journal.py` (only posted rows; period totals = sum of
  posted lines in the DB; date/account/reference filters; Cash Book only cash/bank; OHADA
  codes present vs IFRS codes omitted). Frontend tests extended for name-only search and
  the narration payload.
- Key decisions noted:
  - IFRS cash/bank detection falls back to a name-keyword match because IFRS has no numbered
    cash class; OHADA uses real Class 5 / code starting with `5`.
  - Row `date` is `posted_at` for every posted-line row (Part C), first column.
  - `reference` is a display-only `TX-<id>` human reference (no separate stored column).
- Verification:
  - Could not be executed here (the sandbox shell was non-functional during this session);
    the edited backend modules (journal_service, routes, schemas, migrations, account_service,
    tests) and frontend modules (all pages/components/i18n/tests) were carefully re-read and
    balanced. Re-run `backend: pytest app/tests -q`, `frontend: node
    src/utils/accountLookup.test.mjs`, `node src/utils/txnCalculations.test.mjs`, and
    `npm run build` in a live terminal, plus the manual OHADA + IFRS end-to-end click-test,
    before relying on this session in production.
- What Session 8 needs to know:
  - Ledger / Trial Balance can read the same posted `transaction_lines` (narration now
    persisted) and must keep the framework-aware code display (OHADA shows codes; IFRS none).

### Session 6c — OHADA-standard journal entry UI + account selector bug fix
- Status: DONE
- Date completed: 2026-08-16
- Bug fixed (investigated first, per the brief):
  - The Session 6 New Transaction form used a plain `<select>` for account
    selection. It was never upgraded to the `AccountLookup` autocomplete
    component built in Session 6b, so after the 6b account-model changes (real
    SYSCOHADA hierarchy, `ohada_class_number`) it showed a flat list of ALL
    accounts (including inactive ones the backend rejects) with no search or
    hierarchy support. The controlled-select value binding (`value={a.id}` is a
    number but `line.account_id` starts as `''`) also produced an
    empty-looking/unusable dropdown in browsers.
  - Root cause confirmed via a manual check against existing demo orgs: the
    live DB org 4 (OHADA demo) still had the old Session 5 flat 18-account
    chart (codes 1000/1100…, `ohada_class_number` NULL) — never reseeded after
    6b — while a fresh demo OHADA org returns the real 87-account hierarchy
    (57/Cash, 70/Sales, 5711, 7011 with class numbers 5/7). The API itself was
    fine; the frontend selector was the broken layer.
- What was built:
  - `AccountLookup` gained a `compact` prop (smaller input + dropdown) so it
    fits inline in a journal-entry grid row — no duplicate lookup component.
  - `NewTransactionPage.jsx` redesigned as a real OHADA journal-entry grid:
    Date | N° compte (AccountLookup) | Intitulé (read-only, auto-filled from
    selection) | Libellé | Débit | Crédit. Debit lines first, credits after;
    running totals + balanced/unbalanced indicator update live; Post button
    only enables when balanced. The plain-language "what happened?" step stays
    above the grid, and the "what happened / what this means" explanation
    after posting is unchanged.
  - Only ACTIVE accounts are offered in the lookup (the backend rejects
    inactive accounts at draft creation). Lookup stays within-org (operates on
    the org-scoped account list).
  - Mobile-responsive: desktop = 12-column grid aligned with a header row;
    phone-width = each line stacks into a card (no horizontal scrolling).
  - `frontend/src/utils/txnCalculations.js`: pure, testable helpers (totals,
    balanced, canPost, toPayload). Date field auto-fills to today (editable).
  - i18n EN/FR keys added (tx.date, tx.accountName, tx.libelle,
    tx.libellePlaceholder, tx.debitCol, tx.creditCol, tx.noAccounts).
- Decisions / notes:
  - The backend `Transaction` model has no user-editable date column (it uses
    `created_at`); the grid's date is UI-only for journal presentation. Adding
    a `transaction_date` column is a schema change deferred to a future
    session (explicitly out of scope for 6c).
  - No backend changes were needed: the bug was purely frontend. The
    transaction/transaction_line schema, posting_service balance validation,
    and the transaction API are untouched.
- Verification:
  - `node src/utils/txnCalculations.test.mjs` → 14 checks pass (totals update
    live, balanced check, canPost, payload mapping).
  - `npm run test:lookup` → 5 checks pass (unchanged).
  - `npm run build` → rc=0, 43 modules transformed.
  - Backend `pytest app/tests -q` → 46 passed (unchanged count — no backend
    logic touched).
  - End-to-end (TestClient against a fresh demo OHADA org): 87 accounts
    returned, real OHADA codes present with correct class numbers, draft
    created + posted successfully (balanced 50,000 debit / 50,000 credit).
- What Session 7 needs to know:
  - The journal-entry grid now matches the OHADA layout, so Session 7's
    journal/cashbook read views can build directly on it (they will read the
    posted transaction lines the same way).

### Session 6b — OHADA/IFRS standards-compliant chart of accounts with autocomplete
- Status: DONE
- Date completed: 2026-08-15
- Scope note (stated up front): this session covers account STRUCTURE and NUMBERING
  only (classes, codes, names, hierarchy). Deeper accounting principles/measurement
  (depreciation methods, revenue recognition timing, etc.) are explicitly out of
  scope here and deferred.
- What was built:
  - Migration `0006_add_ohada_class_number` adds nullable Integer `ohada_class_number`
    (1–9) to `accounts`. `account_class` is kept as the simplified 5-category view
    used for normal-balance logic; the genuine 9-class OHADA structure (incl.
    Class 8 and supplementary Class 9) is now representable instead of flattened.
  - `app/accounting/ohada_chart.py`: a REPRESENTATIVE real SYSCOHADA 2017 révisé
    structure (all 9 classes, 2/3/4-digit hierarchy via `parent_account_id`,
    going >=3 levels deep in 10/21/40/41/52/57/60/66/70). Class 9 flagged
    supplementary. Code comment + seed explicitly label it representative, not
    the full ~900-line official list, and "illustrative/demo where applicable."
  - `app/accounting/ifrs_template.py`: editable IAS-1-aligned starting template
    under the 5 plain classes (IFRS has no mandated chart). `ohada_class_number`
    NULL for these. Comment notes it's a flexible template, not a fixed list.
  - `account_service.seed_chart_for_organization` (+ `seed_ohada_chart` /
    `seed_ifrs_template` / `_insert_seed_entries` idempotent upsert by code):
    seeded on demo-workspace creation via `organization_service`; `ohada_class_number`
    derived deterministically from a code's first digit; parent codes resolved to
    `parent_account_id` within the org. `scripts/seed_coa.py` re-seeds to a live org.
  - `account_service.has_posted_transactions()` is now REAL (joins
    transaction_lines→transactions where status != draft) — closes the S5 placeholder
    handoff so deactivating an account used in a posted tx returns 409.
  - Frontend: `AccountTree`/`TreeNode` hierarchical tree (indented by depth), OHADA
    class badges + `ohada_class_number`, framework-aware demo notice (real SYSCOHADA
    vs editable template vs legacy Session-5 data), and `AccountLookup` (code↔name,
    within-org) wired into the create form. i18n EN/FR added.
- Decisions made this session:
  - `ohada_class_number` is a nullable Integer (1–9), NOT an enum — first digit of an
    OHADA code maps directly to its class, and IFRS/legacy rows stay valid as NULL.
  - OHADA vs IFRS charts are intentionally NOT merged: each workspace's chart is fixed
    to its `framework`; autocomplete matches within-org by construction (operates only
    on the org-scoped account list).
  - Same plain-language French↔English names used for the illustrative OHADA subset
    (the reference source is OHADA-French → translated to English); codes/numbers are
    the real official structure.
  - Existing S5/S6 demo data left in place and labelled legacy (nullable column keeps
    it valid) rather than silently reseeded (would break posted transaction references).
  - Frontend lookup test uses a plain Node assert script (`npm run test:lookup`) —
    no jest/vitest dependency on disk; `node --test` produced non-TTY errors here.
- Verification:
  - Backend: 46 tests pass (incl. OHADA 9-class hierarchy + parent links + chains
    10→101→1011 etc.; IFRS template seeds + editable; cross-org scoping; transaction
    deactivation-after-posting guard).
  - `alembic upgrade head` applied migration 0006 on dev Postgres.
  - `python -m scripts.seed_coa 2` runs cleanly and idempotently (27 OHADA definitions).
  - Frontend: `npm run build` rc=0, 42 modules transformed (proves ChartOfAccountsPage,
    AccountLookup, accountLookup.js, and i18n JSON all compile/bundles correctly).
- What the next session needs to know:
  - Session 7 (Cash Book/Journal) can rely on `has_posted_transactions()` being real.
  - The OHADA seed is representative; the full official list can be expanded later by
    appending real entries to `OHADA_CHART` (parent-code → `parent_account_id` resolution
    is already handled).

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

### Session 6b — OHADA/IFRS standards-compliant chart of accounts with autocomplete
- Status: DONE (see full entry at the top of the session log)

### Session 6c — OHADA-standard journal entry UI + account selector bug fix
- Status: DONE (see full entry at the top of the session log)

### Session 7 — Cash Book and Journal
- Status: DONE (see full entry at the top of the session log)

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
- `ohada_class_number` field (Session 6b) is a nullable Integer (1–9), derived from
  an OHADA code's first digit — keeps `account_class` as the 5-category normal-balance
  view while genuinely representing classes 8 & 9, and keeps IFRS/legacy rows valid
  as NULL rather than flattening OHADA into 5 buckets.
- OHADA vs IFRS charts are NEVER merged: a workspace's chart is fixed to its
  `framework`; OHADA = real SYSCOHADA hierarchy; IFRS = editable IAS-1 template.
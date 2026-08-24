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

**Last completed session:** Session 7 follow-up (2) — "real (non-demo) workspaces were empty" fix:
every NEW workspace (demo or not) is auto-seeded with its framework chart, existing non-demo orgs
backfilled via reseed_charts.py, autocomplete upgraded to progressive code-PREFIX narrowing,
"A/C number" label introduced. 54 backend tests green.
**Next session to run:** Session 8 — General Ledger
**Blockers / open questions:** None outstanding. (The `node` CLI cannot execute in this shell —
every invocation fails with "stdout is not a tty" before running any code — so `npm run test:lookup`
must be re-run in a terminal-capable environment. New assertions were cross-validated instead with
an exact Python port of `searchAccounts`; see the Session 7 follow-up (2) entry.)

---

## Session Log

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
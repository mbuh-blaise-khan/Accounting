# Universal Accounting Learning & Practice Platform — Blueprint Summary

> Created in **Session 0**. This is a concise summary of the product blueprint
> that the rest of the MVP is built against. Sections below are deliberately
> short and plain-language; they are the shared reference for every session.

## 1. Product vision

A **bilingual (English/French, Pidgin later)** learning-and-practice web
platform that takes a user from **complete beginner** to **competent, confident
accountant**. It is *both* a place to learn the concepts *and* a real tool where
those concepts actually run — every journal entry, ledger, trial balance and
financial statement is computed by a real, deterministic double-entry engine.

It is **OHADA/IFRS aware**: frameworks are separate, configurable contexts, not
one merged chart of accounts. Default currency is XAF/FCFA (zero decimals), but
currency and precision are stored as configurable fields, never hard-coded.

The product is a **responsive web app** (usable on a phone-width browser from
day one), not a native mobile app.

## 2. The three modes

| Mode | What it does | In MVP? |
|------|--------------|---------|
| **Learn** | Bite-sized lessons + questions that teach accounting concepts in plain language | ✅ Yes (basic, Session 11) |
| **Practice / Bookkeeping** | Enter real transactions and see them flow through journal → ledger → trial balance → statements | ✅ Yes (core, Sessions 6–10) |
| **Analyze / AI** | AI-powered insights, OCR, payments, advanced analytics | ❌ **Not in MVP** (future scope) |

The blueprint's key differentiator: Learn and Practice are **connected** — a
lesson's worked example can actually post a real transaction into the user's
demo workspace so they see the effect in the ledgers/trial balance they built.

## 3. The core accounting chain

A transaction flows through a fixed, deterministic pipeline:

```
transaction  →  journal  →  ledger  →  trial balance  →  financial statements
```

- A **transaction** has ≥ 2 lines; every debit is matched by a credit.
- Posting is **all-or-nothing**: unbalanced transactions are rejected.
- Posted records are **immutable** (only corrected via reversing entries).
- **Ledger balances are derived from posted journal lines** — never stored as a
  separate drift-prone balance.
- Financial statements are **generated from the ledger/trial balance** — never
  manually entered.

## 4. MVP definition

The Minimum Viable Product (end of Session 11) is a used locally, where a user
can:

1. Register and pick English or French (toggle switches instantly).
2. Create a workspace with an OHADA **or** IFRS framework and a currency.
3. Use a small, clearly-labeled **illustrative/demo chart of accounts** (never a
   fabricated "official" OHADA chart).
4. Enter a transaction in plain language and see it posted correctly.
5. Trace that transaction through the **journal → ledger → trial balance →
   financial statements** (income statement + statement of financial position).
6. Work through a few basic lessons with scored questions.
7. Trust it because **automated tests prove accounting integrity** — every
   posted transaction balances, totals always reconcile.

**Out of scope for MVP:** AI tutor, AI-generated content, payments, OCR,
advanced analytics, full official chart-of-accounts data.

## 5. Guardrails

- The accounting engine is **deterministic** — no AI decides a debit/credit
  outcome, ever (now or later).
- Every posted transaction must balance; enforced at the **database/service
  layer**, not only the UI.
- Framework separation: OHADA and IFRS never merge into one generic chart.
- Seed/demo data is labeled "illustrative — replace with reviewed official data
  before production/compliance use."

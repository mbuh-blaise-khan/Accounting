# Universal Accounting Learning & Practice Platform

A bilingual (English / French, Pidgin later) learning-and-practice web platform
for accounting. Built with **React + Tailwind CSS** (frontend), **FastAPI +
SQLAlchemy + Alembic** (backend), and **PostgreSQL** (database).

> 📌 This README is a living document. Session 1 adds the "Getting Started"
> section with exact commands. Tooling and stack details are added as each
> session ships.

## MVP scope (Sessions 0–11)

A local, responsive web app where a user can register, pick a language, create a
workspace (OHADA or IFRS framework), use an illustrative chart of accounts,
enter transactions in plain language, and trace them through journal → ledger →
trial balance → financial statements — plus work through a few basic lessons.
No AI, payments, or advanced analytics in the MVP.

## Repository layout

```
frontend/src/{components,pages,layouts,features,services,hooks,i18n,utils}
backend/app/{api,core,models,schemas,services,repositories,accounting,learning,tests}
backend/alembic/
docs/
scripts/
```

## Docs

- `docs/blueprint-summary.md` — product vision, modes, accounting chain, MVP definition
- `docs/acceptance-criteria.md` — testable acceptance criteria for Sessions 1–11
- `PROGRESS_LOG.md` — session-by-session build history (read before every session)
- `UAP_MVP_Build_Guide_Sessions_0-11.md` — the master build guide

# Universal Accounting Learning & Practice Platform

A bilingual (English / French, Pidgin later) learning-and-practice web platform
for accounting. Built with **React + Tailwind CSS** (frontend), **FastAPI +
SQLAlchemy + Alembic** (backend), and **PostgreSQL** (database).

---

## Getting Started

This walks you through setting up the **three moving parts** — Python backend,
React frontend, and PostgreSQL — on your own machine. Open a terminal at the
project root (`~/Desktop/Accounting`) for each step.

> **Prerequisites:** Python 3.11+ and Node.js 18+ (with npm) installed, and
> PostgreSQL installed and running (see "Install PostgreSQL" below).

### 0. One-time: copy the backend env file

```bash
cd backend
cp .env.example .env        # macOS / Linux
# copy .env.example to .env   # Windows (PowerShell or Explorer)
```

Open `backend/.env` and adjust `DATABASE_URL` to match the user/db you created
below.

### 1. Python backend — virtual environment & dependencies

We put the virtual environment inside `backend/.venv` so it stays local to the
project. You create it once, then activate it whenever you work on the backend.

**Create the venv:**

```bash
# from the project root
python -m venv backend/.venv
```

**Activate it — Windows (Git Bash / MINGW):**

```bash
source backend/.venv/Scripts/activate
```

**Activate it — Windows (PowerShell / CMD):**

```powershell
backend\.venv\Scripts\Activate.ps1    # PowerShell
backend\.venv\Scripts\activate.bat    # CMD
```

**Activate it — macOS / Linux:**

```bash
source backend/.venv/bin/activate
```

When activated, your prompt shows `(.venv)`. **Install dependencies** (do this
once):

```bash
pip install -r backend/requirements.txt
```

**Verify the backend tooling is usable:**

```bash
uvicorn --version
python -c "import fastapi, sqlalchemy; print('backend deps OK')"
```

### 2. PostgreSQL — install, create a database and user

PostgreSQL is **not bundled** with this repo. Install it first if you don't
have it:

```bash
# macOS (Homebrew)
brew install postgresql@16
brew services start postgresql@16

# Ubuntu / Debian
sudo apt update && sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres psql

# Windows
# Use the official EnterpriseDB installer: https://www.postgresql.org/download/windows/
# Accept defaults (a `postgres` superuser and a `5432` port are created).
```

**Create the dev user and database** (adapt the `postgres` superuser password
to yours; use whichever user the installer/`postgres` provided):

```bash
# Linux/macOS (as the postgres user) OR Windows (open psql as the postgres superuser)
psql -U postgres
```

Then, inside the `psql` prompt, run:

```sql
CREATE USER uap WITH PASSWORD 'uap_dev_password';
CREATE DATABASE uap_dev OWNER uap;
GRANT ALL PRIVILEGES ON DATABASE uap_dev TO uap;
\q
```

**Verify you can connect** (from a normal terminal, not inside psql):

```bash
psql -U uap -d uap_dev -h localhost -p 5432
```

When prompted, enter `uap_dev_password`. Type `\q` to exit once connected. This
is the connection check the backend uses, so if this works, `DATABASE_URL`
below is correct:

```
postgresql+psycopg2://uap:uap_dev_password@localhost:5432/uap_dev
```

> On Windows, `psql` may not be on your PATH even after installing. See
> Troubleshooting → "psql: command not found".

### 3. Frontend — install dependencies

```bash
cd frontend
npm install
```

### 4. Run the backend dev server

```bash
# from the project root, with the venv activated (step 1)
uvicorn backend.app.main:app --reload --port 8000
```

- API lives at http://localhost:8000
- Interactive docs at http://localhost:8000/docs

> `backend/app/main.py` is created in **Session 2**. Until then you can verify
> the Python/tooling is installed and healthy with the checks in step 1
> (`uvicorn --version`, `python -c "..."`). Once Session 2 lands, the command
> above runs the real app.

### 5. Run the frontend dev server

```bash
# from a second terminal
cd frontend
npm run dev
```

Open http://localhost:5173 — you should see the placeholder landing page.

---

## Troubleshooting — PostgreSQL connection errors

### "psql: command not found" (Windows)
The PostgreSQL binaries aren't on your `PATH`. Either:
- Add the `bin` folder to PATH, e.g. `C:\Program Files\PostgreSQL\16\bin`, or
- Use **pgAdmin** (installed with PostgreSQL) to create the user/db instead of
  `psql`.

### "could not connect to server: Connection refused"
The PostgreSQL server isn't running. Start it:
```bash
# macOS
brew services start postgresql@16
# Ubuntu/Debian
sudo systemctl start postgresql
# Windows
# Start "postgresql-x64-16" in Services, or use pgAdmin to start the server.
```

### "Password authentication failed for user «uap»"
The password in `backend/.env`'s `DATABASE_URL` doesn't match the user's
password. Re-run the `CREATE USER ... WITH PASSWORD` statement in psql with the
exact password you put in `.env`.

### "database «uap_dev» does not exist"
You created the user but not the database (or used a different name). In `psql
-U postgres`:
```sql
CREATE DATABASE uap_dev OWNER uap;
```

### "role «uap» does not exist"
The user doesn't exist yet. In `psql -U postgres`:
```sql
CREATE USER uap WITH PASSWORD 'uap_dev_password';
```

### "connection to server at localhost, port 5432 failed: No such file or directory"
A Unix socket issue on macOS/Linux; the server isn't running or uses a different
socket. Start the server (see "Connection refused") and/or connect with
`-h localhost` explicitly.

### Windows-specific: `libpq` / DLL errors from psycopg2
`psycopg2-binary` bundles its own libpq, but if you see a
`libpq.dll`/`DLL load failed` error, reinstall it inside the venv:
```bash
pip uninstall psycopg2-binary -y
pip install --force-reinstall psycopg2-binary
```

### `pg_ctl` / `initdb` not found
You installed only the bare client tools, not the full server, or they're not on
PATH. Install the full PostgreSQL server (see install step) and/or add its `bin`
folder to PATH.

---

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



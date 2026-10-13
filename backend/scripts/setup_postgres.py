"""
One-time local Postgres setup -- makes PostgreSQL the actual running
default on this machine, matching the Technical Design Document's
technology choice, without needing administrator rights (no Windows
service; the "installer" .exe needs UAC elevation that a non-interactive
session can't grant, so this uses EDB's portable zip binaries instead).

Idempotent: safe to re-run. Steps:
  1. initdb a data directory under backend/pgdata (skipped if it exists)
  2. start postgres via pg_ctl on PORT (skipped if already running)
  3. create the flync_app role + flync database (skipped if they exist)
  4. write backend/.env with DATABASE_URL -- database.py loads this
     automatically (see load_dotenv() call there), so the app picks
     Postgres up with no shell configuration needed.

Usage: .venv\\Scripts\\python.exe backend\\scripts\\setup_postgres.py
"""
from __future__ import annotations

import secrets
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PG_BIN = ROOT / "backend" / "postgresql" / "pgsql" / "bin"
DATA_DIR = ROOT / "backend" / "pgdata"
LOG_DIR = ROOT / "backend" / "logs"
PORT = 5433  # non-default, so this never collides with a "real" Postgres someone installs later
ENV_FILE = ROOT / "backend" / ".env"


def run(args: list, **kwargs) -> subprocess.CompletedProcess:
    print("+", " ".join(str(a) for a in args))
    return subprocess.run(args, **kwargs)


def psql_scalar(psql: Path, sql: str) -> str:
    result = run(
        [str(psql), "-U", "postgres", "-p", str(PORT), "-h", "127.0.0.1", "-tA", "-c", sql, "postgres"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def main() -> None:
    if not PG_BIN.exists():
        sys.exit(f"PostgreSQL binaries not found at {PG_BIN} -- extract the zip there first "
                  f"(expects backend/postgresql/pgsql/bin/*.exe).")

    initdb, pg_ctl, psql = PG_BIN / "initdb.exe", PG_BIN / "pg_ctl.exe", PG_BIN / "psql.exe"
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if not (DATA_DIR / "PG_VERSION").exists():
        run([str(initdb), "-D", str(DATA_DIR), "-U", "postgres", "-A", "trust", "-E", "UTF8"], check=True)
    else:
        print(f"data dir already initialized at {DATA_DIR}")

    status = run([str(pg_ctl), "-D", str(DATA_DIR), "status"], capture_output=True, text=True)
    if status.returncode != 0:
        run([
            str(pg_ctl), "-D", str(DATA_DIR), "-l", str(LOG_DIR / "postgres.log"),
            "-o", f"-p {PORT} -h 127.0.0.1", "start",
        ], check=True)
        time.sleep(2)
    else:
        print("postgres already running")

    app_password = secrets.token_urlsafe(24)
    role_exists = psql_scalar(psql, "SELECT 1 FROM pg_roles WHERE rolname='flync_app'")
    if role_exists != "1":
        run([str(psql), "-U", "postgres", "-p", str(PORT), "-h", "127.0.0.1", "-c",
             f"CREATE ROLE flync_app LOGIN PASSWORD '{app_password}'", "postgres"], check=True)
    else:
        # Role already exists from a previous run -- reset its password so
        # this script's own DATABASE_URL (written below) is always correct.
        run([str(psql), "-U", "postgres", "-p", str(PORT), "-h", "127.0.0.1", "-c",
             f"ALTER ROLE flync_app PASSWORD '{app_password}'", "postgres"], check=True)

    db_exists = psql_scalar(psql, "SELECT 1 FROM pg_database WHERE datname='flync'")
    if db_exists != "1":
        run([str(psql), "-U", "postgres", "-p", str(PORT), "-h", "127.0.0.1", "-c",
             "CREATE DATABASE flync OWNER flync_app", "postgres"], check=True)
    else:
        print("database 'flync' already exists")

    database_url = f"postgresql+psycopg2://flync_app:{app_password}@127.0.0.1:{PORT}/flync"
    ENV_FILE.write_text(f"DATABASE_URL={database_url}\n", encoding="utf-8")
    print(f"\nWrote {ENV_FILE} -- backend will use Postgres on next start.")
    print(f"Postgres data dir: {DATA_DIR}")
    print(f"To stop it later:  {pg_ctl} -D \"{DATA_DIR}\" stop")
    print(f"To start it again: {pg_ctl} -D \"{DATA_DIR}\" -o \"-p {PORT} -h 127.0.0.1\" start")


if __name__ == "__main__":
    main()

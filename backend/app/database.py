"""
Couche de persistance -- PostgreSQL par défaut désormais (matching the
Technical Design Document's technology choice), via backend/.env written
by scripts/setup_postgres.py. Retombe sur SQLite si Postgres n'a jamais
été configuré sur cette machine (portable, zéro-config). Garde EXACTEMENT
la même API publique (init_db, save_run, get_run, list_runs, save_items,
get_items) -- donc aucun autre fichier du backend (routers, services)
n'a besoin de changer.

Nouveau : log_audit_event / get_audit_log -- historique versionné de
chaque run (le "History & Audit Log" du document d'architecture), qui
n'existait pas du tout avant.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

ROOT = Path(__file__).resolve().parents[2]

# Loads backend/.env if present (e.g. the DATABASE_URL written by
# scripts/setup_postgres.py) without requiring it to be exported in the
# shell -- a no-op if the file doesn't exist, so nothing changes for
# anyone who *does* export DATABASE_URL themselves or has no .env at all.
load_dotenv(ROOT / "backend" / ".env")

# Postgres by default (see scripts/setup_postgres.py) : DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/flync
# Falls back to the same zero-config SQLite file if Postgres was never set up.
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{ROOT / 'backend' / 'flync.sqlite3'}")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class RunRow(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    current_step: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[str | None] = mapped_column(String, nullable=True)
    completed_at: Mapped[str | None] = mapped_column(String, nullable=True)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    logs: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    scenario_count: Mapped[int] = mapped_column(Integer, default=0)
    script_count: Mapped[int] = mapped_column(Integer, default=0)


class RunItemRow(Base):
    """Table générique qui remplace 'scenarios' et 'scripts' -- `kind`
    distingue les deux, exactement comme le paramètre `table` de
    l'ancienne API save_items(table, run_id, items)."""
    __tablename__ = "run_items"
    kind: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, ForeignKey("runs.id"), primary_key=True)
    item_id: Mapped[str] = mapped_column(String, primary_key=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)  # JSON


class UserRow(Base):
    """Accounts for the JWT-based auth layer (see auth.py). Seeded with two
    demo accounts on first startup -- see init_db()."""
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String, primary_key=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="qa_engineer")
    created_at: Mapped[str] = mapped_column(String, nullable=False)


class AuditLogRow(Base):
    """Nouveau -- 'History & Audit Log' du document d'architecture.
    Un événement par étape marquante d'un run (créé, Phase1 terminé,
    Phase2 terminé, échec, coverage gap-filled...). Jamais modifié ni
    supprimé après écriture -- c'est un journal, pas un état."""
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str | None] = mapped_column(String, ForeignKey("runs.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)


def init_db() -> None:
    if DATABASE_URL.startswith("sqlite"):
        (ROOT / "backend").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    _seed_default_users()


def reconcile_orphaned_runs() -> None:
    """Startup crash-recovery -- per the Technical Design Document §9's
    "stateless Back-End services" goal: a run's live execution lives in a
    `threading.Thread` inside one process (see pipeline_service.py). If
    that process dies mid-run (crash, kill, restart), the run is left
    stuck at status="running"/"pending" forever with nothing to ever move
    it forward -- any replica reading it from the DB would show a run
    that looks eternally "in progress". Called once at startup: whatever
    was already "running"/"pending" when THIS process started could not
    possibly have been started by this process, so it's marked failed
    instead of silently rotting."""
    now = datetime.now(timezone.utc).isoformat()
    with SessionLocal() as session:
        orphaned = session.query(RunRow).filter(RunRow.status.in_(["running", "pending"])).all()
        for row in orphaned:
            row.status = "failed"
            row.current_step = "failed"
            row.error = "Interrupted: backend process restarted while this run was in progress."
            row.completed_at = now
        session.commit()
        run_ids = [row.id for row in orphaned]

    for run_id in run_ids:
        log_audit_event(run_id, "run_orphaned", "Marked failed: backend restarted mid-run")


def _seed_default_users() -> None:
    """First-run only: creates two demo accounts so the app is usable
    without a separate registration flow. Printed once, loudly, so the
    credentials are easy to find in the backend's own log."""
    with SessionLocal() as session:
        if session.query(UserRow).count() > 0:
            return

    from .auth import hash_password  # local import: avoids a circular import at module load

    demo_users = [
        ("qa@flync.io", "flync123", "QA Engineer", "qa_engineer"),
        ("admin@flync.io", "admin123", "Platform Admin", "administrator"),
    ]
    for email, password, full_name, role in demo_users:
        create_user(email, hash_password(password), full_name, role)

    print("[auth] Seeded demo accounts (change these before any real deployment):")
    for email, password, _full_name, role in demo_users:
        print(f"[auth]   {email} / {password}  ({role})")


def save_run(run: dict[str, Any]) -> None:
    with SessionLocal() as session:
        existing = session.get(RunRow, run["id"])
        payload = {
            "id": run["id"], "status": run["status"], "current_step": run["current_step"],
            "created_at": run["created_at"], "started_at": run.get("started_at"),
            "completed_at": run.get("completed_at"),
            "requirements": json.dumps(run.get("requirements", {})),
            "error": run.get("error"), "logs": json.dumps(run.get("logs", [])),
            "scenario_count": run.get("scenario_count", 0), "script_count": run.get("script_count", 0),
        }
        if existing is None:
            session.add(RunRow(**payload))
        else:
            for key, value in payload.items():
                setattr(existing, key, value)
        session.commit()

    log_audit_event(run["id"], "run_saved", f"status={run['status']} step={run['current_step']}")


def get_run(run_id: str) -> dict[str, Any] | None:
    with SessionLocal() as session:
        row = session.get(RunRow, run_id)
        if row is None:
            return None
        return {
            "id": row.id, "status": row.status, "current_step": row.current_step,
            "created_at": row.created_at, "started_at": row.started_at, "completed_at": row.completed_at,
            "requirements": json.loads(row.requirements), "error": row.error,
            "logs": json.loads(row.logs), "scenario_count": row.scenario_count, "script_count": row.script_count,
        }


def list_runs() -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = session.query(RunRow).order_by(RunRow.created_at.desc()).all()
        ids = [row.id for row in rows]
    return [get_run(run_id) for run_id in ids]


def save_items(table: str, run_id: str, items: list[dict[str, Any]]) -> None:
    with SessionLocal() as session:
        for item in items:
            existing = session.get(RunItemRow, {"kind": table, "run_id": run_id, "item_id": item["id"]})
            if existing is None:
                session.add(RunItemRow(kind=table, run_id=run_id, item_id=item["id"], payload=json.dumps(item)))
            else:
                existing.payload = json.dumps(item)
        session.commit()

    log_audit_event(run_id, f"{table}_saved", f"{len(items)} item(s)")


def get_items(table: str, run_id: str) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        rows = (
            session.query(RunItemRow)
            .filter(RunItemRow.kind == table, RunItemRow.run_id == run_id)
            .order_by(RunItemRow.item_id)
            .all()
        )
        return [json.loads(row.payload) for row in rows]


def create_user(email: str, hashed_password: str, full_name: str, role: str = "qa_engineer") -> dict[str, Any]:
    with SessionLocal() as session:
        row = UserRow(
            email=email, hashed_password=hashed_password, full_name=full_name,
            role=role, created_at=datetime.now(timezone.utc).isoformat(),
        )
        session.add(row)
        session.commit()
    return get_user_by_email(email)  # type: ignore[return-value]


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with SessionLocal() as session:
        row = session.get(UserRow, email)
        if row is None:
            return None
        return {
            "email": row.email, "hashed_password": row.hashed_password,
            "full_name": row.full_name, "role": row.role, "created_at": row.created_at,
        }


def log_audit_event(run_id: str | None, event_type: str, message: str) -> None:
    with SessionLocal() as session:
        session.add(AuditLogRow(
            run_id=run_id, event_type=event_type, message=message,
            created_at=datetime.now(timezone.utc).isoformat(),
        ))
        session.commit()


def get_audit_log(run_id: str | None = None) -> list[dict[str, Any]]:
    with SessionLocal() as session:
        query = session.query(AuditLogRow).order_by(AuditLogRow.id.desc())
        if run_id is not None:
            query = query.filter(AuditLogRow.run_id == run_id)
        return [
            {"id": r.id, "run_id": r.run_id, "event_type": r.event_type, "message": r.message, "created_at": r.created_at}
            for r in query.limit(500).all()
        ]
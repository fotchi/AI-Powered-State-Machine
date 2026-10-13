"""
Administrator-only: "monitoring of AI workflow duration and success rate"
(Technical Design Document §9). Derived from the run history that was
already being persisted (RunRow.status/started_at/completed_at) but never
aggregated or exposed anywhere.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from ..auth import require_admin
from ..database import list_runs

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromisoformat(ts)


@router.get("")
def get_metrics(_admin: dict = Depends(require_admin)):
    runs = list_runs()

    completed = [r for r in runs if r["status"] == "completed"]
    failed = [r for r in runs if r["status"] == "failed"]
    in_progress = [r for r in runs if r["status"] in ("pending", "running")]
    finished = completed + failed

    durations = []
    for run in finished:
        started, ended = _parse(run["started_at"]), _parse(run["completed_at"])
        if started and ended:
            durations.append((ended - started).total_seconds())
    durations.sort()

    def _percentile(values: list[float], pct: float) -> float | None:
        if not values:
            return None
        index = min(len(values) - 1, int(round(pct * (len(values) - 1))))
        return round(values[index], 1)

    return {
        "total_runs": len(runs),
        "completed": len(completed),
        "failed": len(failed),
        "in_progress": len(in_progress),
        "success_rate": round(len(completed) / len(finished), 3) if finished else None,
        "avg_duration_seconds": round(sum(durations) / len(durations), 1) if durations else None,
        "p95_duration_seconds": _percentile(durations, 0.95),
    }

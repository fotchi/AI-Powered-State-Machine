from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from ..database import save_items, save_run
from ..logging_config import logger
from .phase1_service import run_phase1
from .phase2_service import run_phase2
from ..realtime import publish

# How often (in log lines) to flush `run["logs"]` to the DB while a stage is
# streaming subprocess output, instead of only at the 3 coarse checkpoints
# below. Keeps a crashed process from losing more than a few lines of
# history for whatever the next-to-read replica needs to display.
LOG_FLUSH_EVERY = 5


def start_pipeline(requirements: dict[str, Any]) -> dict[str, Any]:
    run = {
        "id": str(uuid.uuid4()), "status": "pending", "current_step": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "started_at": None, "completed_at": None, "requirements": requirements,
        "error": None, "logs": [], "scenario_count": 0, "script_count": 0,
    }
    save_run(run)
    publish(run["id"], {"type": "run_created", "run": run})
    threading.Thread(target=_execute, args=(run["id"],), daemon=True).start()
    return run


def _make_on_log(run: dict[str, Any], run_id: str, step: str):
    """Publishes every line live (as before) and additionally persists
    `run["logs"]` to the DB every LOG_FLUSH_EVERY lines, so a crash mid-stage
    loses at most a handful of lines instead of everything since the last
    coarse checkpoint."""
    count = 0

    def on_log(message: str) -> None:
        nonlocal count
        publish(run_id, {"type": "log", "step": step, "message": message})
        count += 1
        if count % LOG_FLUSH_EVERY == 0:
            save_run(run)

    return on_log


def _execute(run_id: str) -> None:
    from ..database import get_run
    run = get_run(run_id)
    if run is None:
        return
    logger.info(f"run {run_id}: started")
    try:
        run.update(status="running", current_step="scenario_agent", started_at=datetime.now(timezone.utc).isoformat())
        save_run(run)
        publish(run_id, {"type": "step_started", "step": "scenario_agent", "status": run["status"]})
        scenarios = run_phase1(run["logs"], _make_on_log(run, run_id, "scenario_agent"), requirements=run.get("requirements"))
        save_items("scenarios", run_id, scenarios)
        run.update(current_step="script_agent", scenario_count=len(scenarios))
        save_run(run)
        logger.info(f"run {run_id}: scenario agent complete ({len(scenarios)} scenarios)")
        publish(run_id, {"type": "scenario_agent_complete", "step": "scenario_agent", "scenario_count": len(scenarios), "logs": run["logs"][-20:]})
        scripts = run_phase2(run_id, scenarios, run["logs"], _make_on_log(run, run_id, "script_agent"))
        save_items("scripts", run_id, scripts)
        run.update(status="completed", current_step="completed", script_count=len(scripts))
        logger.info(f"run {run_id}: completed ({len(scripts)} scripts)")
        publish(run_id, {"type": "pipeline_complete", "step": "completed", "scenario_count": len(scenarios), "script_count": len(scripts), "logs": run["logs"][-20:]})
    except Exception as exc:
        run.update(status="failed", current_step="failed", error=str(exc))
        run["logs"].append(f"[Backend] ERROR: {exc}")
        logger.exception(f"run {run_id}: failed")
        publish(run_id, {"type": "pipeline_failed", "step": "failed", "error": str(exc), "logs": run["logs"][-20:]})
    finally:
        run["completed_at"] = datetime.now(timezone.utc).isoformat()
        save_run(run)

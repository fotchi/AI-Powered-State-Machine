import subprocess

from fastapi import APIRouter, HTTPException, Query

from ..database import get_items, get_run
from ..services.phase2_service import execute_all_scripts, execute_existing_script, read_existing_outputs

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.get("")
def get_scripts(run_id: str | None = Query(default=None)):
    if run_id and get_run(run_id) is None:
        raise HTTPException(404, "Run not found")
    scripts = get_items("scripts", run_id) if run_id else read_existing_outputs()
    return {"run_id": run_id, "scripts": scripts}


@router.get("/{script_id}")
def get_script(script_id: str, run_id: str | None = Query(default=None)):
    scripts = get_items("scripts", run_id) if run_id else read_existing_outputs()
    for script in scripts:
        if script["id"] == script_id:
            return script
    raise HTTPException(404, "Script not found")


@router.post("/{script_id}/execute")
def execute_script(script_id: str):
    try:
        return execute_existing_script(script_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(408, "Script execution timed out") from exc
    except Exception as exc:
        raise HTTPException(500, f"Script execution failed: {exc}") from exc


@router.post("/execute-all")
def execute_all():
    # Sequential, ~1s/script (Python startup + FLYNC model import, no real
    # I/O in the generated scripts themselves) -- for the current ~117-script
    # backlog that's roughly a couple of minutes, well within a plain
    # blocking POST (same pattern as /coverage/{id}/fill).
    try:
        return execute_all_scripts()
    except Exception as exc:
        raise HTTPException(500, f"Bulk execution failed: {exc}") from exc

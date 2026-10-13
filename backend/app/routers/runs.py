from fastapi import APIRouter, HTTPException

from ..database import get_run, list_runs
from ..services.pipeline_service import start_pipeline
from ..schemas import RunCreate, RunResponse

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunResponse, status_code=202)
def create_run(request: RunCreate):
    run = start_pipeline(request.requirements)
    return RunResponse(run_id=run["id"], status=run["status"], current_step=run["current_step"])


@router.get("", response_model=list[dict])
def get_runs():
    return list_runs()


@router.get("/{run_id}")
def get_run_status(run_id: str):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return run

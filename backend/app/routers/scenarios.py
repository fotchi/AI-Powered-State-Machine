from fastapi import APIRouter, HTTPException, Query

from ..database import get_items, get_run
from ..services.phase1_service import read_existing_outputs

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("")
def get_scenarios(run_id: str | None = Query(default=None)):
    if run_id and get_run(run_id) is None:
        raise HTTPException(404, "Run not found")
    scenarios = get_items("scenarios", run_id) if run_id else read_existing_outputs()
    return {"run_id": run_id, "scenarios": scenarios}


@router.get("/{scenario_id}")
def get_scenario(scenario_id: str, run_id: str | None = Query(default=None)):
    scenarios = get_items("scenarios", run_id) if run_id else read_existing_outputs()
    for scenario in scenarios:
        if scenario["id"] == scenario_id:
            return scenario
    raise HTTPException(404, "Scenario not found")

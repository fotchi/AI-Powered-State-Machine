"""
Administrator-only: exposes the "History & Audit Log" (database.py's
log_audit_event/get_audit_log) over the API. Restricted to the
"administrator" role -- the concrete example of the Technical Design
Document's "role-based access control for QA vs. administrative actions".
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..auth import require_admin
from ..database import get_audit_log

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
def list_audit_log(run_id: str | None = Query(default=None), _admin: dict = Depends(require_admin)):
    return {"events": get_audit_log(run_id)}

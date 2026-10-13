"""
Nouveau router, indépendant du reste -- expose l'Object Store côté API.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..artifact_sync import sync_all
from ..database import log_audit_event
from ..object_store import get_object, list_objects

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.post("/sync")
def sync_artifacts():
    """Copie les scripts du Script Agent + la doc du Scenario Agent déjà sur disque vers
    l'Object Store (S3 ou fallback local)."""
    result = sync_all()
    log_audit_event(None, "artifacts_synced", f"{result}")
    return result


@router.get("")
def list_artifacts(prefix: str = ""):
    return {"keys": list_objects(prefix)}


@router.get("/{key:path}")
def download_artifact(key: str):
    content = get_object(key)
    if content is None:
        raise HTTPException(404, f"Artifact not found: {key}")
    media_type = "text/x-python" if key.endswith(".py") else "application/octet-stream"
    return Response(content=content, media_type=media_type)
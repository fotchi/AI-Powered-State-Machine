"""
Synchronise les artefacts bruts déjà produits par le Scenario Agent / Script Agent vers
l'Object Store -- ne génère rien, se contente de copier ce qui existe
déjà sur disque vers le store versionnable (S3 ou fallback local).
"""
from __future__ import annotations

from pathlib import Path

from .object_store import put_object

ROOT = Path(__file__).resolve().parents[2]
PHASE2_SCRIPTS = ROOT / "phase2" / "generated_scripts_"
PHASE1_DOCS = ROOT / "phase1" / "data" / "flync_docs"


def sync_scripts() -> dict[str, int]:
    """Copie chaque script .py de phase2/generated_scripts_/ vers
    scripts/<category>/<id>.py dans l'Object Store."""
    count = 0
    if PHASE2_SCRIPTS.exists():
        for path in PHASE2_SCRIPTS.rglob("*.py"):
            category = path.parent.name
            key = f"scripts/{category}/{path.stem}.py"
            put_object(key, path.read_bytes(), content_type="text/x-python")
            count += 1
    return {"scripts_synced": count}


def sync_docs() -> dict[str, int]:
    """Copie la doc FLYNC locale (téléchargée par le Scenario Agent) vers docs/ dans
    l'Object Store -- utile pour garder une trace versionnée de la doc
    utilisée pour une génération donnée."""
    count = 0
    if PHASE1_DOCS.exists():
        for path in PHASE1_DOCS.rglob("*"):
            if path.is_file():
                key = f"docs/{path.relative_to(PHASE1_DOCS)}".replace("\\", "/")
                put_object(key, path.read_bytes())
                count += 1
    return {"docs_synced": count}


def sync_all() -> dict[str, int]:
    result = sync_scripts()
    result.update(sync_docs())
    return result
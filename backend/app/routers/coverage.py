"""
Nouveau router, complètement séparé de scenarios.py/scripts.py/runs.py --
n'importe et ne modifie rien de l'existant.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..subprocess_env import PHASE1_KEYS, minimal_env

ROOT = Path(__file__).resolve().parents[3]
PHASE1_ROOT = ROOT / "phase1"

router = APIRouter(prefix="/coverage", tags=["coverage"])


def _run_cli(action: str, machine_key: str, timeout: int) -> dict:
    # "report" is read-only but now makes one LLM call per machine for the
    # semantic coverage check (matcher.py -> semantic_matcher.py); "fill"
    # calls phase1's LLM router per detected gap. Both need PHASE1_KEYS.
    result = subprocess.run(
        [sys.executable, "coverage_cli.py", action, machine_key],
        cwd=PHASE1_ROOT,
        env=minimal_env(PHASE1_KEYS, PYTHONPATH=str(ROOT)),
        capture_output=True, text=True, timeout=timeout,
        encoding="utf-8", errors="replace",
    )
    stdout_lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    if not stdout_lines:
        raise HTTPException(500, f"coverage_cli.py produced no output. stderr: {result.stderr}")

    try:
        payload = json.loads(stdout_lines[-1])
    except json.JSONDecodeError:
        raise HTTPException(500, f"coverage_cli.py returned non-JSON output: {stdout_lines[-1]!r}. stderr: {result.stderr}")

    if "error" in payload:
        raise HTTPException(404, payload["error"])
    return payload


@router.get("/machines")
def list_machines():
    """Les 12 State Machines disponibles (proposition d'architecture révisée,
    d'architecture), avec le module Scenario Agent réel associé à chacune."""
    result = subprocess.run(
        [sys.executable, "coverage_cli.py", "list"],
        cwd=PHASE1_ROOT, env=minimal_env(PYTHONPATH=str(ROOT)),
        capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace",
    )
    stdout_lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    if not stdout_lines:
        raise HTTPException(500, f"coverage_cli.py produced no output. stderr: {result.stderr}")
    return json.loads(stdout_lines[-1])


@router.get("/machines/describe")
def describe_machines():
    """Full structure (states, on_pass/on_fail transitions, coverage_tags)
    of all 12 State Machines -- powers the State Machine explorer screen,
    which renders this real architecture instead of a mock diagram."""
    result = subprocess.run(
        [sys.executable, "coverage_cli.py", "describe-all"],
        cwd=PHASE1_ROOT, env=minimal_env(PYTHONPATH=str(ROOT)),
        capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace",
    )
    stdout_lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    if not stdout_lines:
        raise HTTPException(500, f"coverage_cli.py produced no output. stderr: {result.stderr}")
    return json.loads(stdout_lines[-1])


@router.get("/consistency")
def get_consistency():
    """L' "Integration Agent" du document d'architecture -- vérifie que
    chaque scénario du Scenario Agent a bien un script du Script Agent correspondant, et
    signale les orphelins dans l'autre sens. Lecture seule."""
    result = subprocess.run(
        [sys.executable, "coverage_cli.py", "consistency"],
        cwd=PHASE1_ROOT, env=minimal_env(PYTHONPATH=str(ROOT)),
        capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace",
    )
    stdout_lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    if not stdout_lines:
        raise HTTPException(500, f"coverage_cli.py produced no output. stderr: {result.stderr}")
    return json.loads(stdout_lines[-1])


@router.get("/{machine_key}")
def get_coverage(machine_key: str):
    # Lecture seule (rien n'est écrit), mais matcher.py fait maintenant UN
    # appel LLM par machine pour juger la couverture par le sens plutôt que
    # par mot-clé littéral seul (voir semantic_matcher.py). Un appel isolé
    # prend generalement quelques secondes, mais on a mesuré jusqu'a ~11s
    # meme sans contention (charge du compte Groq partage), et un
    # TimeoutExpired ici casse la connexion sans les entetes CORS -- le
    # navigateur l'affiche alors a tort comme une erreur CORS, masquant la
    # vraie cause. 60s laisse une vraie marge plutot que de coller au plus
    # juste observe.
    return _run_cli("report", machine_key, timeout=60)


@router.post("/{machine_key}/fill")
def fill_coverage(machine_key: str):
    # 1 appel LLM par trou détecté -- peut prendre plusieurs minutes.
    return _run_cli("fill", machine_key, timeout=900)
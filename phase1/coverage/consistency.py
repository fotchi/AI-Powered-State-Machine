"""
Formalise le rôle de "Integration Agent" décrit dans le Technical Design
Document (section 4) : "merges both outputs, checks scenario-to-script
consistency, and flags gaps".

Contrairement au coverage engine (matcher.py, qui compare une State
Machine théorique à ce qui existe), ce module compare directement les
DEUX sorties réelles entre elles :
- phase1/output/scenarios_submodels.json + scenarios_cross_module.json
- phase2/generated_scripts_/**/*.py

Purement en lecture -- ne génère rien, ne modifie rien (contrairement à
gap_filler.py). "Flags gaps", ne les comble pas.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PHASE1_OUTPUT = ROOT / "phase1" / "output"
PHASE2_SCRIPTS = ROOT / "phase2" / "generated_scripts_"


def _load_all_scenarios() -> list[dict[str, Any]]:
    scenarios = []
    for filename in ("scenarios_submodels.json", "scenarios_cross_module.json"):
        path = PHASE1_OUTPUT / filename
        if path.exists():
            scenarios.extend(json.loads(path.read_text(encoding="utf-8")).get("scenarios", []))
    return scenarios


def _expected_script_id(scenario: dict[str, Any]) -> str:
    """Reproduit exactement le schéma de nommage du Script Agent
    (script_<id en minuscules avec tirets->underscores>_<positive|neg_negative>)."""
    slug = scenario["id"].lower().replace("-", "_")
    suffix = "positive" if scenario.get("type", "").lower() == "positive" else "neg_negative"
    return f"script_{slug}_{suffix}"


def _existing_script_ids() -> set[str]:
    if not PHASE2_SCRIPTS.exists():
        return set()
    return {path.stem for path in PHASE2_SCRIPTS.rglob("*.py")}


def check_consistency() -> dict[str, Any]:
    scenarios = _load_all_scenarios()
    existing_script_ids = _existing_script_ids()

    expected_ids = {_expected_script_id(s): s["id"] for s in scenarios}

    missing_scripts = [
        {"scenario_id": scenario_id, "expected_script_id": expected_id}
        for expected_id, scenario_id in expected_ids.items()
        if expected_id not in existing_script_ids
    ]
    orphan_scripts = sorted(existing_script_ids - set(expected_ids))

    return {
        "total_scenarios": len(scenarios),
        "total_scripts": len(existing_script_ids),
        "consistent": len(scenarios) - len(missing_scripts),
        "missing_scripts": missing_scripts,
        "orphan_scripts": orphan_scripts,
    }
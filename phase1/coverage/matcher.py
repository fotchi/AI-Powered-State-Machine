"""
Compare les cas théoriques (engine.enumerate_expected_cases) à ce qui
existe RÉELLEMENT dans output/scenarios_submodels.json pour le submodel
Scenario Agent associé à une State Machine, et retourne les trous.

Chaque State Machine porte son propre "phase1_module" (voir state_machines/
*.py) -- plusieurs machines peuvent pointer vers le même agent réel (ex:
CAN_MACHINE et LIN_MACHINE pointent toutes les deux vers 'bus').

Deux passes : (1) mot-clé littéral (rapide, gratuit, précis quand il
matche), (2) pour tout ce que (1) ne trouve pas, UN SEUL appel LLM par
machine (semantic_matcher.judge_coverage_via_llm) qui juge par le SENS --
un scénario qui décrit "MDI/MII configuration is present" couvre bien la
règle "ecu.fields" même s'il n'utilise jamais le mot "field", ce que (1)
seul ratait systématiquement (cf. limites documentées avec le pilote ECU).
Si l'appel LLM échoue (pas de clé, réseau), on garde le résultat de (1)
seul -- jamais d'erreur remontée à l'utilisateur pour autant.
"""
from __future__ import annotations

import json
import os
from typing import Any

from phase1.coverage.engine import enumerate_expected_cases
from phase1.coverage.semantic_matcher import case_key, judge_coverage_via_llm

SUBMODELS_OUTPUT_PATH = "output/scenarios_submodels.json"


def _load_existing_for_module(phase1_module: str) -> list[dict[str, Any]]:
    submodel_full_name = f"flync_4_{phase1_module}"
    if not os.path.exists(SUBMODELS_OUTPUT_PATH):
        return []
    with open(SUBMODELS_OUTPUT_PATH, encoding="utf-8") as f:
        payload = json.load(f)
    return [s for s in payload.get("scenarios", []) if s.get("submodel") == submodel_full_name]


def _is_covered(case: dict[str, str], existing_scenarios: list[dict[str, Any]]) -> bool:
    keyword = case["tag"].split(".")[-1]  # "can.bus_ref" -> "bus_ref"
    for s in existing_scenarios:
        haystack = f"{s.get('title','')} {s.get('description','')} {s.get('injected_fault') or ''}".lower()
        if keyword.replace("_", " ") in haystack or keyword in haystack:
            return True
    return False


def coverage_report(machine: dict[str, Any]) -> dict[str, Any]:
    phase1_module = machine["phase1_module"]
    existing = _load_existing_for_module(phase1_module)
    expected = enumerate_expected_cases(machine)

    literal_gaps = [case for case in expected if not _is_covered(case, existing)]

    verdicts = judge_coverage_via_llm(machine["id"], literal_gaps, existing) if literal_gaps else {}
    semantic_ran = verdicts is not None
    verdicts = verdicts or {}

    gaps = [case for case in literal_gaps if not verdicts.get(case_key(case), False)]

    return {
        "machine": machine["id"],
        "phase1_module": phase1_module,
        "expected_total": len(expected),
        "covered": len(expected) - len(gaps),
        "gaps": gaps,
        "verification_method": "keyword+llm" if semantic_ran else "keyword",
    }
"""
Niveau 3 du document -- "Test Mutation Machine" : parcourt une State
Machine et énumère, pour chaque état testable (qui a un coverage_tag),
le cas PASS attendu et le cas FAIL attendu.

C'est purement mécanique : ça ne regarde PAS ce qui existe déjà, juste
"qu'est-ce qui DEVRAIT exister en théorie si on couvrait tout".
"""
from __future__ import annotations

from typing import Any


def enumerate_expected_cases(machine: dict[str, Any]) -> list[dict[str, str]]:
    """Retourne une liste de cas théoriques, ex:
    [{"tag": "ecu.fields", "state": "VALIDATE_ECU_FIELDS", "expected_outcome": "PASS"},
     {"tag": "ecu.fields", "state": "VALIDATE_ECU_FIELDS", "expected_outcome": "FAIL_REQUIRED"},
     ...]
    Un état sans coverage_tag est ignoré (c'est un état purement
    structurel de la chaîne, pas un point de test à couvrir)."""
    cases: list[dict[str, str]] = []
    for state_id, transitions in machine["states"].items():
        tag = transitions.get("coverage_tag")
        if not tag:
            continue
        cases.append({"tag": tag, "state": state_id, "expected_outcome": "PASS"})
        cases.append({"tag": tag, "state": state_id, "expected_outcome": transitions["on_fail"]})
    return cases
"""
La "glue" : pour chaque trou détecté par matcher.coverage_report, construit
une requirement synthétique et appelle single_run.run_single -- LE MÊME
mécanisme que le formulaire "Generate Scenario" utilise déjà (donc même
garanties : ID qui continue la numérotation, pas d'écrasement, appel LLM
skippé si le nom existe déjà).
"""
from __future__ import annotations

from typing import Any

from phase1.coverage.matcher import coverage_report
from phase1.single_run import run_single, ScenarioAlreadyExistsError


def _case_title(case: dict[str, str]) -> str:
    """Génère un titre lisible à partir du tag et du résultat attendu,
    ex: ('can.bus_ref', 'FAIL_REFERENCE') -> 'CAN bus ref - FAIL_REFERENCE'.
    Générique, fonctionne pour n'importe quelle State Machine sans
    entretenir une table de titres à la main pour chaque cas."""
    object_name, field = case["tag"].split(".", 1)
    readable_field = field.replace("_", " ")
    if case["expected_outcome"] == "PASS":
        return f"Valid {object_name.upper()} {readable_field}"
    return f"{object_name.upper()} {readable_field} -> {case['expected_outcome']}"


def _case_to_requirements(phase1_module: str, case: dict[str, str]) -> dict[str, Any]:
    scenario_type = "positive" if case["expected_outcome"] == "PASS" else "negative"
    return {
        "name": _case_title(case),
        "module": phase1_module,
        "description": (
            f"Cover coverage_tag '{case['tag']}' at state '{case['state']}' "
            f"with expected outcome '{case['expected_outcome']}'."
        ),
        "scenarioType": scenario_type,
        "n_scenarios": 1,
    }


def fill_coverage_gaps(machine: dict[str, Any]) -> dict[str, Any]:
    """Retourne un résumé : combien de trous détectés, combien générés
    avec succès, et le détail de chaque tentative (utile pour les logs
    streamés au frontend). Un trou qui échoue n'empêche pas les suivants."""
    report = coverage_report(machine)
    phase1_module = machine["phase1_module"]
    results = []
    new_scenarios: list[dict[str, Any]] = []

    for index, case in enumerate(report["gaps"], start=1):
        # Progress line for the streamed pipeline logs (a fill of several
        # gaps runs minutes with no other output between LLM calls).
        print(f"[gap_filler] gap {index}/{len(report['gaps'])}: {case['tag']} ({case['expected_outcome']})", flush=True)
        requirements = _case_to_requirements(phase1_module, case)
        try:
            scenarios = run_single(requirements)
            new_scenarios.extend(sc.to_dict() for sc in scenarios)
            results.append({
                "case": case, "status": "generated",
                "scenario_ids": [s.id for s in scenarios],
            })
        except ScenarioAlreadyExistsError as exc:
            results.append({"case": case, "status": "already_existed", "detail": str(exc)})
        except Exception as exc:  # noqa: BLE001 -- on continue les autres trous même si un échoue
            results.append({"case": case, "status": "failed", "detail": str(exc)})

    return {
        "machine": machine["id"],
        "phase1_module": phase1_module,
        "gaps_detected": len(report["gaps"]),
        "generated": sum(1 for r in results if r["status"] == "generated"),
        "results": results,
        "scenarios": new_scenarios,
    }
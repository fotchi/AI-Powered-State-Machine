"""
Génération ciblée : un seul submodel + une requirement custom venant du
formulaire "Generate Scenario" du frontend (name/description/preconditions/
expectedBehavior), au lieu de relancer tout le pipeline (11 agents +
cross-module) comme le fait main.py.

Utilisé par le backend quand `requirements` contient un module reconnu.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from phase1.agents.llm_router import LLMRouter
from phase1.agents import (
    app_agent, bus_agent, communication_agent, ecu_agent, metadata_agent,
    nm_agent, security_agent, signal_agent, someip_agent, topology_agent, tsn_agent,
)

# Clés attendues côté frontend (dropdown "Module / Feature") -> agent réel.
# Garde les clés en minuscule : le frontend envoie ce qu'il veut, on normalise.
AGENTS_BY_KEY = {
    "app": app_agent,
    "bus": bus_agent,
    "communication": communication_agent,
    "ecu": ecu_agent,
    "metadata": metadata_agent,
    "nm": nm_agent,
    "security": security_agent,
    "signal": signal_agent,
    "someip": someip_agent,
    "topology": topology_agent,
    "tsn": tsn_agent,
}

SUBMODELS_OUTPUT_PATH = "output/scenarios_submodels.json"


class ScenarioAlreadyExistsError(Exception):
    """Levée quand un scénario du même nom existe déjà pour ce submodel --
    permet à l'appelant (gap_filler.py, le formulaire "Generate Scenario")
    de sauter l'appel LLM au lieu de payer pour un quasi-doublon."""


def _load_existing_scenarios() -> list[dict[str, Any]]:
    if not os.path.exists(SUBMODELS_OUTPUT_PATH):
        return []
    with open(SUBMODELS_OUTPUT_PATH, encoding="utf-8") as f:
        return json.load(f).get("scenarios", [])


def _submodel_full_name(module_key: str) -> str:
    return f"flync_4_{module_key}"


def _name_already_exists(module_key: str, name: str) -> bool:
    if not name:
        return False
    submodel_full_name = _submodel_full_name(module_key)
    name_norm = name.strip().lower()
    return any(
        s.get("submodel") == submodel_full_name and str(s.get("title", "")).strip().lower() == name_norm
        for s in _load_existing_scenarios()
    )


def _next_index_for_submodel(module_key: str) -> int:
    """Reprend la numérotation SC-<SUB>-NNN là où elle s'est arrêtée pour ce
    submodel, au lieu de repartir de 001 à chaque appel (ce que fait
    base_agent.py tout seul en fallback quand le LLM ne fournit pas d'id)."""
    prefix = f"SC-{module_key.upper()}-"
    max_index = 0
    for s in _load_existing_scenarios():
        sid = str(s.get("id", ""))
        if sid.startswith(prefix) and sid[len(prefix):].isdigit():
            max_index = max(max_index, int(sid[len(prefix):]))
    return max_index + 1


def _renumber_to_continue(scenarios: list, module_key: str) -> None:
    """Réassigne les ids générés pour qu'ils continuent la numérotation
    existante -- évite toute collision avec des scénarios déjà présents."""
    next_index = _next_index_for_submodel(module_key)
    for offset, scenario in enumerate(scenarios):
        scenario.id = f"SC-{module_key.upper()}-{next_index + offset:03d}"


def run_single(requirements: dict[str, Any]) -> list:
    """requirements attendu (envoyé par ScenarioGeneration.tsx) :
    {name, module, description, scenarioType, priority, preconditions,
     expectedBehavior, tags, n_scenarios?}

    `module` doit être une des clés de AGENTS_BY_KEY (voir mise à jour du
    dropdown frontend). Lève ValueError si le module est inconnu -- le
    backend renvoie ça comme erreur de run plutôt que de planter en silence.

    Si un scénario du même `name` existe déjà pour ce submodel, lève
    ScenarioAlreadyExistsError SANS appeler le LLM (voir gap_filler.py qui
    dépend de ce comportement pour ne pas régénérer les trous déjà comblés).
    """
    module_key = str(requirements.get("module", "")).strip().lower()
    agent_module = AGENTS_BY_KEY.get(module_key)
    if agent_module is None:
        raise ValueError(
            f"Module inconnu: '{requirements.get('module')}'. "
            f"Valeurs attendues: {sorted(AGENTS_BY_KEY)}"
        )

    name = str(requirements.get("name", "")).strip()
    if _name_already_exists(module_key, name):
        raise ScenarioAlreadyExistsError(
            f"Un scénario nommé '{name}' existe déjà pour le submodel '{module_key}' -- appel LLM ignoré."
        )

    custom_requirement = _build_custom_requirement_text(requirements)
    scenario_type = str(requirements.get("scenarioType", "both")).lower()
    if scenario_type not in ("positive", "negative", "both"):
        scenario_type = "both"

    llm_router = LLMRouter()
    agent = agent_module.build_agent(llm_router)
    scenarios = agent.generate_scenarios(
        n_scenarios=int(requirements.get("n_scenarios", 4)),
        custom_requirement=custom_requirement,
        scenario_type=scenario_type,
    )

    if not scenarios:
        raise RuntimeError(
            f"Aucun scénario généré pour le module '{module_key}' "
            f"(scenario_type={scenario_type}). Vérifie les logs LLM ci-dessus."
        )

    _renumber_to_continue(scenarios, module_key)
    _merge_into_submodels_output(scenarios)
    return scenarios


def _build_custom_requirement_text(requirements: dict[str, Any]) -> str:
    parts = []
    if requirements.get("name"):
        parts.append(f"Scenario name: {requirements['name']}")
    if requirements.get("description"):
        parts.append(f"Description: {requirements['description']}")
    if requirements.get("preconditions"):
        parts.append(f"Preconditions: {requirements['preconditions']}")
    if requirements.get("expectedBehavior"):
        parts.append(f"Expected behavior: {requirements['expectedBehavior']}")
    if requirements.get("tags"):
        parts.append(f"Tags: {requirements['tags']}")
    return "\n".join(parts)


def _merge_into_submodels_output(new_scenarios: list) -> None:
    """Ajoute les nouveaux scénarios au fichier de sortie existant, en
    dédupliquant par id (un id déjà présent est écrasé par la nouvelle
    version). Ne touche pas au fichier cross-module. C'est ce fichier que
    le Script Agent et le backend (read_existing_outputs) lisent -- donc les
    nouveaux scénarios apparaissent immédiatement dans l'app, sans
    attendre un run complet du pipeline batch."""
    path = SUBMODELS_OUTPUT_PATH
    payload: dict[str, Any] = {"metadata": {}, "scenarios": []}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)

    existing = {s["id"]: s for s in payload.get("scenarios", [])}
    for s in new_scenarios:
        existing[s.id] = s.to_dict()

    payload["scenarios"] = list(existing.values())
    payload.setdefault("metadata", {})
    payload["metadata"]["generated_at"] = datetime.now(timezone.utc).isoformat()
    payload["metadata"]["total_scenarios"] = len(payload["scenarios"])

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
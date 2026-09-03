#!/usr/bin/env python3
"""
orchestrateur_langgraph.py
=============================
Orchestrateur du pipeline FLYNC (§4 du cahier des charges) — relie les
quatre agents déjà en place :

    kb_pointers / kb_discovery
        -> pointeurs + cartographie du dépôt FLYNC (12 modules).
    agent_lecteur_analyste.py (AgentLecteurAnalyste)
        -> analyse indépendante de chaque module (classes, champs,
           validators réels).
    scenario_verifier.py (verify_scenario, KBIndex)
        -> pour un scénario KPIT donné, trouve la/les classe(s) réelles
           concernées + leurs validators.
    agent_developpeur.py (generate_llm_script / generate_construction_script)
        -> génère le script Python autonome (contrat d'exit code
           Positive/Negative, cf. agent_developpeur.py).

Ce fichier ajoute la dernière étape : EXÉCUTER réellement chaque script
généré, lire son exit code, et si ça échoue, renvoyer l'erreur au LLM pour
qu'il corrige — jusqu'à --max-retries tentatives, puis abandon (le
scénario est marqué ÉCHEC dans le rapport final, mais le pipeline continue
avec les scénarios suivants).

BOUCLE PAR SCÉNARIO (implémentée comme un petit graphe LangGraph) :

    developpeur -> executer -> evaluer --[retry]--> developpeur
                                        --[fin]---> (fin du scénario)

  * node_developpeur : génère le script (LLM ou template selon --mode),
    l'écrit sur disque. Si le LLM échoue à produire un code syntaxiquement
    valide (LLMGenerationError, cf. agent_developpeur.py), repli
    automatique sur le mode template pour cette tentative.
  * node_executer : lance le script avec `python script.py` dans un
    sous-processus (PYTHONPATH pointant sur le dépôt KB cloné, pour que
    les `from flync.model...` réels fonctionnent), capture stdout/stderr/
    exit code.
  * node_evaluer : applique le contrat d'exit code (agent_developpeur.py)
    pour décider PASS/FAIL :
      - Positive : PASS si exit==0 ET "SUCCESS" dans stdout.
      - Negative : PASS si exit==0 ET "EXPECTED ERROR" dans stdout.
      - tout le reste (exit!=0, crash, sortie inattendue) : FAIL.
    Si FAIL et qu'il reste des tentatives : construit un message de
    feedback (stdout+stderr) et boucle vers node_developpeur. Sinon : fin.

Le graphe est compilé UNE fois (il ne dépend pas du scénario), puis invoqué
une fois par scénario dans une boucle Python classique dans `main()` — pas
besoin d'un graphe géant qui boucle sur tous les scénarios, chaque
scénario est indépendant des autres.

USAGE :
    python orchestrateur_langgraph.py --scenarios kpit_scenarios.json \
        --mode llm --output-dir generated_scripts_final --max-retries 2

    python orchestrateur_langgraph.py --scenarios kpit_scenarios.json \
        --mode template --output-dir generated_scripts_final --max-retries 2
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, TypedDict

from langgraph.graph import StateGraph, END

from third_step.agent_developpeur import (
    LLMGenerationError,
    _resolve_matched_classes,
    generate_construction_script,
    generate_llm_script,
    get_llm,
)
from second_step.agent_lecteur_analyste import AgentLecteurAnalyste, ClassInfo
from first_step.kb_pointers import FLYNC_KB
from module_relations import build_module_relation_graph
from third_step.scenario_verifier import KBIndex, verify_scenario


# ---------------------------------------------------------------------------
# Etat du graphe (un etat par scenario, independant des autres scenarios)
# ---------------------------------------------------------------------------

class ScenarioState(TypedDict, total=False):
    scenario: dict
    matched_classes: list[ClassInfo]
    validators_by_class: dict[str, list[str]]
    submodels_actually_linked: Optional[bool]
    script_path: Path
    code: str
    attempt: int
    max_retries: int
    feedback: Optional[str]
    stdout: str
    stderr: str
    returncode: int
    status: str  # "PASS" | "FAIL" (rempli par node_evaluer)
    used_template_fallback: bool


# ---------------------------------------------------------------------------
# Contexte partagé (construit une fois dans main(), capture par closure
# dans les fonctions-noeuds -- class_lookup/llm/repo_dir sont identiques
# pour tous les scenarios d'un meme run).
# ---------------------------------------------------------------------------

class Contexte:
    def __init__(self, class_lookup: dict[str, ClassInfo], llm, mode: str, repo_dir: Path, output_dir: Path):
        self.class_lookup = class_lookup
        self.llm = llm
        self.mode = mode
        self.repo_dir = repo_dir
        self.output_dir = output_dir


def _make_nodes(ctx: Contexte):
    """Ferme les fonctions-noeuds sur `ctx` (evite les variables globales)."""

    def node_developpeur(state: ScenarioState) -> ScenarioState:
        scenario = state["scenario"]
        matched_classes = state["matched_classes"]
        validators_by_class = state["validators_by_class"]
        submodels_actually_linked = state.get("submodels_actually_linked")
        attempt = state.get("attempt", 0) + 1
        feedback = state.get("feedback")
        used_fallback = False

        if ctx.mode == "template":
            code, warnings = generate_construction_script(
                scenario, matched_classes, validators_by_class, ctx.class_lookup,
                submodels_actually_linked=submodels_actually_linked,
            )
            for w in warnings:
                print(f"[orchestrateur] AVERTISSEMENT: {w}")
        else:
            try:
                code = generate_llm_script(
                    scenario, matched_classes, validators_by_class, ctx.class_lookup,
                    ctx.llm, feedback=feedback,
                    submodels_actually_linked=submodels_actually_linked,
                )
            except LLMGenerationError as exc:
                print(f"[orchestrateur] {exc} -> repli template pour cette tentative.")
                code, warnings = generate_construction_script(
                    scenario, matched_classes, validators_by_class, ctx.class_lookup,
                    submodels_actually_linked=submodels_actually_linked,
                )
                for w in warnings:
                    print(f"[orchestrateur] AVERTISSEMENT: {w}")
                used_fallback = True

        func_id = re.sub(r"[^a-z0-9_]", "_", scenario["id"].lower())
        script_path = ctx.output_dir / f"script_{func_id}.py"
        script_path.write_text(code, encoding="utf-8")

        return {
            **state,
            "code": code,
            "script_path": script_path,
            "attempt": attempt,
            "used_template_fallback": used_fallback,
        }

    def node_executer(state: ScenarioState) -> ScenarioState:
        import os

        env = dict(os.environ)
        # Les scripts generes importent `from flync.model....` -- il faut
        # que le package top-level `flync` (attendu sous <repo>/src/flync)
        # soit sur le PYTHONPATH du sous-processus. Hypothese de layout
        # standard (src/flync/...) coherente avec model_root_path utilise
        # par agent_lecteur_analyste.py -- a ajuster si votre depot a une
        # disposition differente.
        src_dir = str(ctx.repo_dir / "src")
        env["PYTHONPATH"] = src_dir + os.pathsep + env.get("PYTHONPATH", "")

        try:
            result = subprocess.run(
                [sys.executable, str(state["script_path"])],
                capture_output=True, text=True, timeout=30, env=env,
            )
            stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = (exc.stderr or "") + "\n[orchestrateur] TIMEOUT: le script a dépassé 30s."
            returncode = 1

        return {**state, "stdout": stdout, "stderr": stderr, "returncode": returncode}

    def node_evaluer(state: ScenarioState) -> ScenarioState:
        scenario = state["scenario"]
        scenario_id = scenario["id"]
        scenario_type = scenario["type"]
        stdout, stderr, returncode = state["stdout"], state["stderr"], state["returncode"]

        if scenario_type == "Positive":
            status = "PASS" if returncode == 0 and "SUCCESS" in stdout else "FAIL"
        else:  # Negative
            status = "PASS" if returncode == 0 and "EXPECTED ERROR" in stdout else "FAIL"

        print(f"\n===== {scenario_id} : {'RÉUSSI' if status == 'PASS' else 'ÉCHEC'} (exit={returncode}) =====")
        if status == "FAIL":
            if stdout.strip():
                print(stdout.rstrip())
            if stderr.strip():
                print(stderr.rstrip())
        print("=================")

        feedback = None
        if status == "FAIL":
            feedback = (
                f"Le script précédent a échoué à l'exécution réelle "
                f"(exit code {returncode}, attendu 0 pour ce scénario {scenario_type}).\n"
                f"STDOUT :\n{stdout.strip() or '(vide)'}\n\n"
                f"STDERR :\n{stderr.strip() or '(vide)'}"
            )

        return {**state, "status": status, "feedback": feedback}

    return node_developpeur, node_executer, node_evaluer


def _route_apres_evaluation(state: ScenarioState) -> str:
    if state["status"] == "PASS":
        return "fin"
    if state["attempt"] >= state["max_retries"] + 1:
        return "fin"
    return "retry"


def build_graph(ctx: Contexte):
    node_developpeur, node_executer, node_evaluer = _make_nodes(ctx)

    graph = StateGraph(ScenarioState)
    graph.add_node("developpeur", node_developpeur)
    graph.add_node("executer", node_executer)
    graph.add_node("evaluer", node_evaluer)

    graph.set_entry_point("developpeur")
    graph.add_edge("developpeur", "executer")
    graph.add_edge("executer", "evaluer")
    graph.add_conditional_edges("evaluer", _route_apres_evaluation, {"retry": "developpeur", "fin": END})

    return graph.compile()


# ---------------------------------------------------------------------------
# Point d'entree
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Orchestrateur LangGraph du pipeline FLYNC.")
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--mode", choices=["template", "llm"], default="template")
    parser.add_argument("--llm-backend", choices=["ollama", "anthropic", "gemini"], default=None)
    parser.add_argument("--max-retries", type=int, default=2,
                         help="Tentatives max (génération + exécution) avant d'abandonner un scénario "
                              "en échec, appliqué en mode template ET en mode llm (défaut: 2).")
    parser.add_argument("--output-dir", default="./generated_scripts_final")
    args = parser.parse_args()

    scenarios_data = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
    scenarios = scenarios_data["scenarios"]

    print("[orchestrateur] Analyse de la KB via l'Agent Lecteur/Analyste ...")
    agent = AgentLecteurAnalyste(FLYNC_KB)
    full_report = agent.run()

    class_lookup: dict[str, ClassInfo] = {}
    for module_analysis in full_report.modules.values():
        for class_name, class_info in module_analysis.classes.items():
            class_lookup.setdefault(class_name, class_info)

    kb_index = KBIndex(agent.repo_dir)
    kb_index.build_from_model(agent, full_report)
    kb_index.build_from_sdk()

    relation_graph = build_module_relation_graph(full_report)
    print(f"[orchestrateur] Graphe de relations inter-modules : {relation_graph.total_edges} lien(s), "
          f"{len(relation_graph.bridge_class_index)} classe(s)-pont.")

    llm = get_llm(args.llm_backend) if args.mode == "llm" else None

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    ctx = Contexte(class_lookup, llm, args.mode, agent.repo_dir, output_dir)
    app = build_graph(ctx)

    resultats: dict[str, str] = {}

    for scenario in scenarios:
        verdict = verify_scenario(scenario, kb_index, class_lookup, relation_graph)
        matched_classes = _resolve_matched_classes(verdict, class_lookup)

        if verdict.classification == "REQUIRES_SDK":
            print(f"[orchestrateur] {scenario['id']}: REQUIRES_SDK -> hors périmètre, ignoré.")
            resultats[scenario["id"]] = "IGNORÉ (REQUIRES_SDK)"
            continue

        etat_initial: ScenarioState = {
            "scenario": scenario,
            "matched_classes": matched_classes,
            "validators_by_class": verdict.validators_on_matched_classes,
            "submodels_actually_linked": verdict.submodels_actually_linked,
            "attempt": 0,
            "max_retries": args.max_retries,
            "feedback": None,
        }

        etat_final = app.invoke(etat_initial)
        status = etat_final["status"]
        attempts = etat_final["attempt"]
        resultats[scenario["id"]] = f"{status} (après {attempts} tentative(s))"

    print("\n[orchestrateur] Terminé. Résultats :")
    n_pass = sum(1 for r in resultats.values() if r.startswith("PASS"))
    for scenario_id, r in resultats.items():
        print(f"  {scenario_id}: {r}")
    print(f"\n[orchestrateur] {n_pass}/{len(resultats)} scénario(s) en PASS.")

    return 0 if n_pass == len(resultats) else 1


if __name__ == "__main__":
    raise SystemExit(main())
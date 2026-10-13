"""
agent_developpeur_cross.py
============================
Agent Développeur Cross-Module (LLM uniquement -- pas de repli gabarit).

Traite EXCLUSIVEMENT des scénarios KPIT impliquant plusieurs sous-modèles
FLYNC. Contrairement à l'Agent Mono-Module, il n'a aucun chemin template :
si le LLM échoue après N tentatives, le scénario reste en échec et est
marqué pour relecture manuelle.

BUGS CORRIGÉS :
  [FIX-1] --mode ignoré mais accepté dans argparse (compatibilité CLI avec
           le mono-module, qui l'expose comme argument obligatoire dans les
           scripts d'automatisation existants).
  [FIX-2] Doublon de print + variable morte 'last_error' supprimés dans
           generate_llm_script_cross (REVUE-3 symétrique au mono-module).
  [FIX-3] validators_by_class : accès à l'attribut correct sur ValidatorInfo
           (.name au lieu de .method_name, qui n'existe pas sur ClassInfo).
  [FIX-4] valider_imports_flync et valider_kwargs_autorises branchés dans
           la boucle de validation/retry (FIX-5 / FIX-6 du commun.py v4,
           déjà présents dans le mono mais manquants ici).
  [FIX-5] known_modules passé à valider_imports_flync (nécessite ctx).
"""

from __future__ import annotations

import argparse
import concurrent.futures
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from phase2.src.flync_pipeline.etape2_lecteur.agent_lecteur_analyste import ClassInfo, FieldInfo
from phase2.src.flync_pipeline.etape2_lecteur.module_relations import ModuleRelationGraph
from phase2.src.flync_pipeline.etape3_verificateur.scenario_verifier import verify_scenario, ScenarioVerdict

from .commun import (
    DEFAULT_EXECUTION_TIMEOUT_SECONDS,
    LLMGenerationError,
    ScenarioProcessingResult,
    SharedContext,
    build_shared_context,
    classes_potentiellement_necessaires,
    execute_generated_script,
    extract_scenario_values,
    extraire_code_python,
    format_execution_error,
    format_scenario_values_block,
    get_llm,
    load_scenarios,
    output_path_for,
    resolve_matched_classes,
    valider_classes_autorisees,
    valider_contrat_negative,
    valider_fidelite_valeurs,
    valider_imports_flync,
    valider_kwargs_autorises,
    valider_syntaxe,
)

AGENT_LABEL = "agent-dev-cross"

DEFAULT_CROSS_TIMEOUT_SECONDS = 45
DEFAULT_CROSS_MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Résolution des classes-pont
# ---------------------------------------------------------------------------

def _bridge_context_for(
    submodels: list[str],
    relation_graph: ModuleRelationGraph,
    class_lookup: dict[str, ClassInfo],
) -> tuple[set[str], str]:
    """Retourne (classes-pont réelles, texte de couplage pour le prompt LLM)."""
    bridges: set[str] = set()
    reasons: list[str] = []
    for i in range(len(submodels)):
        for j in range(i + 1, len(submodels)):
            a, b = submodels[i], submodels[j]
            for cls_name, modules in relation_graph.bridge_class_index.items():
                if {a, b} <= modules and cls_name in class_lookup:
                    bridges.add(cls_name)
            for (src, dst), why in relation_graph.edge_reasons.items():
                if {src, dst} == {a, b}:
                    reasons.append(f"{src} -> {dst} : {', '.join(sorted(why))}")
    reason_text = (
        "\n".join(reasons) if reasons
        else "(aucun couplage AST réel trouvé entre ces sous-modèles)"
    )
    return bridges, reason_text


# ---------------------------------------------------------------------------
# Résolution des champs (héritage MRO simplifié)
# ---------------------------------------------------------------------------

def _resolve_all_fields(
    class_info: ClassInfo,
    class_lookup: dict[str, ClassInfo],
) -> list[FieldInfo]:
    seen: set[str] = set()
    result: list[FieldInfo] = []

    def _walk(ci: ClassInfo) -> None:
        for base in ci.bases:
            bi = class_lookup.get(base)
            if bi:
                _walk(bi)
        for f in ci.fields:
            if f.name not in seen:
                seen.add(f.name)
                result.append(f)

    _walk(class_info)
    return result


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

@dataclass
class CrossScenarioPlan:
    scenario: dict
    verdict: ScenarioVerdict
    matched_names: list[str]   # entités du Vérificateur + classes-pont forcées
    bridge_reason: str
    category: str              # "cross_module" | "requires_sdk" | "unresolved"


def classify_cross_scenario(
    scenario: dict,
    kb_index,
    class_lookup: dict[str, ClassInfo],
    relation_graph: ModuleRelationGraph,
    retriever,
) -> CrossScenarioPlan:
    verdict = verify_scenario(scenario, kb_index, class_lookup, relation_graph, retriever)
    submodels = verdict.submodels_declared

    if len(submodels) < 2:
        print(
            f"[{AGENT_LABEL}] INCOHÉRENCE: {scenario['id']} vient du fichier "
            f"cross-module mais submodel='{scenario['submodel']}' ne déclare "
            f"qu'un seul sous-modèle. Traité quand même -- à corriger côté KPIT."
        )

    bridges, bridge_reason = _bridge_context_for(submodels, relation_graph, class_lookup)
    matched_names = sorted(set(verdict.entities_found_in_model) | bridges)

    if verdict.classification == "REQUIRES_SDK":
        category = "requires_sdk"
    elif not matched_names:
        category = "unresolved"
    else:
        category = "cross_module"

    return CrossScenarioPlan(
        scenario=scenario, verdict=verdict,
        matched_names=matched_names, bridge_reason=bridge_reason,
        category=category,
    )


def _print_classification_report(plans: list[CrossScenarioPlan]) -> None:
    counts: dict[str, int] = {}
    bridged = 0
    for p in plans:
        counts[p.category] = counts.get(p.category, 0) + 1
        if set(p.matched_names) - set(p.verdict.entities_found_in_model):
            bridged += 1
    print(f"\n[{AGENT_LABEL}] ===== Rapport de classification (0 appel LLM) =====")
    for category in ("cross_module", "requires_sdk", "unresolved"):
        print(f"[{AGENT_LABEL}]   {category:14s} : {counts.get(category, 0)}")
    print(f"[{AGENT_LABEL}]   dont complétés par classe(s)-pont : {bridged}")
    print(f"[{AGENT_LABEL}] " + "=" * 58 + "\n")


# ---------------------------------------------------------------------------
# Prompt LLM (cross-module)
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_LLM_CROSS = (
    "Tu es un générateur de code Python pour le framework FLYNC (modèles "
    "Pydantic v2 réels, pas une simulation). Le scénario que tu reçois est "
    "CROSS-MODULE : il implique des classes appartenant à au moins deux "
    "sous-modules FLYNC différents, et la faute ou le comportement décrit "
    "peut dépendre d'une relation ENTRE ces classes, pas d'une seule "
    "classe isolée.\n\n"
    "FORMAT DE RÉPONSE, ABSOLU ET NON NÉGOCIABLE :\n"
    "- Ta réponse ENTIÈRE doit être un unique bloc ```python ... ``` et rien "
    "d'autre. Aucune phrase avant, aucune phrase après, aucune explication, "
    "aucun commentaire (#), aucune docstring.\n\n"
    "MÉCANISMES DE RELATION CROSS-MODULE RÉELS DANS FLYNC :\n"
    "A) RÉFÉRENCE TYPÉE : un champ a directement pour type une autre classe "
    "(ou List[AutreClasse]) -- Pydantic valide la structure automatiquement.\n"
    "B) RÉFÉRENCE TEXTUELLE (fréquente) : un champ `List[str]` ou `str` "
    "porte un nom qui doit correspondre au champ `name` d'un objet défini "
    "ailleurs. Non vérifiée par Pydantic sur l'objet feuille -- résolue par "
    "un @model_validator sur un agrégat de plus haut niveau. CONSÉQUENCE : "
    "construis l'agrégat qui contient et résout cette référence, pas "
    "seulement l'objet feuille.\n\n"
    "RÈGLES DE CONTENU :\n"
    "1. PAS DE TEST : jamais pytest/assert/pytest.raises/test_*().\n"
    "2. Instancie TOUTES les classes listées (y compris les [PONT]).\n"
    "3. Valeurs concrètes. Valeurs du bloc VALEURS DU SCÉNARIO TELLES QUELLES.\n"
    "4. N'invente JAMAIS un champ, une classe ou un validator non listés.\n"
    "4bis. N'IMPORTE PAS puis REDÉFINIS une classe FLYNC.\n"
    "4ter. [ENUM] : référence un membre, n'instancie jamais avec ().\n\n"
    "COUPLAGE RÉEL ENTRE LES SOUS-MODÈLES :\n"
    "5. Si 'Couplage AST réel' = aucun → construis les objets indépendamment, "
    "sans inventer de liaison.\n"
    "6. Si un couplage est trouvé → la classe-pont DOIT apparaître dans "
    "ta construction.\n\n"
    "CONTRAT D'EXIT CODE :\n"
    "- `import sys` = TOUJOURS la première ligne.\n"
    "- Positive : construction directe SANS try/except → print(\"SUCCESS\") → sys.exit(0).\n"
    "- Negative : `from pydantic import ValidationError`, construction de "
    "l'AGRÉGAT dans try/except/else, sys.exit(0) dans except ValidationError "
    "UNIQUEMENT, sys.exit(1) dans else et tout autre except.\n\n"
    "GARDE-FOUS :\n"
    "7. Ne suppose jamais qu'une ValidationError sera levée sans mécanisme réel.\n"
    "8. Aucune simulation : pas de classe locale, stub ou validator custom.\n"
    "9. Si la faute nécessite plusieurs objets, construis-les TOUS.\n\n"
    "VALIDATION RÉELLE :\n"
    "10. Ce script est RÉELLEMENT EXÉCUTÉ. Aucun repli gabarit n'existe : "
    "si tu épuises tes tentatives, le scénario reste en échec."
)


def _construire_prompt_humain_cross(
    scenario: dict,
    matched_classes: list[ClassInfo],
    bridge_names: set[str],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
    submodels: list[str],
    bridge_reason: str,
    feedback: Optional[str],
    resolved_via_rag: Optional[list[str]] = None,
) -> str:
    resolved_via_rag = resolved_via_rag or []
    blocks: list[str] = []
    import_lines: list[str] = []

    for ci in matched_classes:
        all_fields = _resolve_all_fields(ci, class_lookup)
        field_lines: list[str] = []
        for f in all_fields:
            constraint = (
                f" | contrainte réelle: {f.default_str}"
                if f.default_str and "Field(" in (f.default_str or "")
                else ""
            )
            referenced = class_lookup.get(f.type_str.strip())
            type_note = ""
            if referenced is not None and referenced.is_enum:
                type_note = (
                    f" | [ENUM, membres: "
                    f"{', '.join(referenced.enum_members) or 'aucun détecté'}]"
                )
            elif f.type_str.strip().startswith(("List[str]", "list[str]", "str")):
                type_note = (
                    " | [RÉFÉRENCE TEXTUELLE POSSIBLE -- "
                    "lis mécanisme B du prompt système]"
                )
            field_lines.append(
                f"  - {f.name}: {f.type_str} | "
                f"obligatoire={f.required}{constraint}{type_note}"
            )

        class_validators = [
            v for v in validators_by_class.get(ci.name, [])
            if v != "(aucun validator)"
        ]
        notes: list[str] = []
        if ci.name in bridge_names:
            notes.append(
                "[PONT: cette classe matérialise le couplage réel "
                "entre les sous-modules déclarés]"
            )
        if ci.name in resolved_via_rag:
            notes.append(
                "[NOTE: résolue par similarité sémantique (RAG), "
                "confiance modérée]"
            )
        note_str = ("\n" + " ".join(notes)) if notes else ""
        blocks.append(
            f"{ci.name} (module réel: {ci.module}, fichier: {ci.file})"
            f"{note_str}\n"
            f"Champs (avec héritage résolu) :\n"
            + "\n".join(field_lines) + "\n"
            f"Validators réels sur cette classe : "
            f"{class_validators or '(aucun)'}"
        )
        stem = ci.file.removesuffix(".py")
        import_lines.append(
            f"from flync.model.{ci.module}.{stem} import {ci.name}"
        )

    classes_desc = (
        "\n\n".join(blocks) if blocks
        else "aucune classe résolue, même après injection des classes-pont"
    )
    imports_hint = (
        "\n".join(import_lines) if import_lines
        else "# aucun import déterminable automatiquement"
    )

    scenario_values = extract_scenario_values(scenario)
    values_block = format_scenario_values_block(scenario_values)

    human = (
        f"Scénario : {scenario['id']} ({scenario['type']})\n"
        f"Sous-modèles déclarés : {', '.join(submodels)}\n"
        f"Titre : {scenario['title']}\n"
        f"Description : {scenario['description']}\n"
        f"Fault injecté : {scenario.get('injected_fault')}\n"
        f"Résultat attendu : {scenario['expected_result']}\n\n"
        f"Couplage AST réel détecté entre ces sous-modèles :\n"
        f"{bridge_reason}\n\n"
        f"Imports réels à utiliser :\n{imports_hint}\n\n"
        f"Classe(s) disponible(s) ({len(matched_classes)}) :\n"
        f"{classes_desc}\n\n"
        f"{values_block}\n\n"
        f"Rappel : réponds UNIQUEMENT avec un bloc ```python contenant le "
        f"script complet, sans aucun texte avant/après, sans commentaire, "
        f"en commençant par `import sys`."
    )
    if feedback:
        human += (
            f"\n\nFEEDBACK D'UNE EXÉCUTION PRÉCÉDENTE "
            f"(corrige le script généré) :\n{feedback}"
        )
    return human


# ---------------------------------------------------------------------------
# Génération LLM
# ---------------------------------------------------------------------------

def generate_llm_script_cross(
    scenario: dict,
    matched_classes: list[ClassInfo],
    bridge_names: set[str],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
    llm,
    flync_src_root: Path,
    submodels: list[str],
    bridge_reason: str,
    feedback: Optional[str] = None,
    max_retries: int = DEFAULT_CROSS_MAX_RETRIES,
    resolved_via_rag: Optional[list[str]] = None,
    timeout_seconds: int = DEFAULT_CROSS_TIMEOUT_SECONDS,
    known_modules: Optional[set[str]] = None,
) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    human_prompt = _construire_prompt_humain_cross(
        scenario, matched_classes, bridge_names, validators_by_class,
        class_lookup, submodels, bridge_reason, feedback, resolved_via_rag,
    )
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT_LLM_CROSS),
        HumanMessage(content=human_prompt),
    ]
    allowed_names = classes_potentiellement_necessaires(matched_classes, class_lookup)

    scenario_values = extract_scenario_values(scenario)
    known_field_names: set[str] = set()
    for ci in matched_classes:
        known_field_names |= {f.name for f in _resolve_all_fields(ci, class_lookup)}

    attempt_errors: list[tuple[int, str, str]] = []

    for attempt in range(1, max_retries + 2):
        response = llm.invoke(messages)
        code = extraire_code_python(response.content)

        error, kind = None, ""

        if error is None:
            error = valider_syntaxe(code)
            kind = "syntaxe"

        if error is None:
            error = valider_classes_autorisees(code, allowed_names)
            kind = "classes hors périmètre / shadowing"

        # [FIX-4] valider_kwargs_autorises branché (manquait vs mono-module)
        if error is None:
            error = valider_kwargs_autorises(code, matched_classes, class_lookup)
            kind = "kwarg halluciné sur constructeur FLYNC"

        # [FIX-4] valider_imports_flync branché (manquait vs mono-module)
        if error is None:
            error = valider_imports_flync(code, known_modules, class_lookup)
            kind = "import module/fichier/symbole halluciné"

        if error is None and scenario.get("type") == "Negative":
            error = valider_contrat_negative(code)
            kind = "contrat exit-code Negative violé"

        if error is None:
            exec_result = execute_generated_script(
                code, flync_src_root, timeout_seconds=timeout_seconds
            )
            if not exec_result.success:
                error = format_execution_error(exec_result)
                kind = "exécution réelle"

        if error is None:
            error = valider_fidelite_valeurs(code, scenario_values, known_field_names)
            kind = "valeurs du scénario non respectées"

        if error is None:
            return code

        # [FIX-2] Une seule entrée dans l'historique + un seul print, pas deux
        attempt_errors.append((attempt, kind, error))
        print(
            f"[{AGENT_LABEL}] {scenario['id']}: {kind} invalide "
            f"(tentative {attempt}) -> {error}"
        )
        messages.append(response)
        messages.append(HumanMessage(content=(
            f"Le code précédent est rejeté ({kind}) : {error}\n"
            f"Renvoie UNIQUEMENT le code Python corrigé, sous forme d'un unique "
            f"bloc ```python, en commençant par `import sys`, sans aucun texte "
            f"hors du code, sans commentaire. Rappel : aucun repli n'existe pour "
            f"ce scénario cross-module -- corrige le mécanisme de relation si "
            f"c'est la cause de l'échec, ne le supprime pas."
        )))

    kinds_seen = [k for _, k, _ in attempt_errors]
    repeated = len(set(kinds_seen)) == 1 and len(kinds_seen) > 1
    history = "\n".join(
        f"  tentative {a}: [{k}] {m}" for a, k, m in attempt_errors
    )
    suffix = (
        " (même type d'erreur -- hallucination probablement stable)"
        if repeated else ""
    )
    raise LLMGenerationError(
        f"{scenario['id']}: échec après {max_retries + 1} tentative(s)"
        f"{suffix}.\n{history}"
    )


# ---------------------------------------------------------------------------
# Traitement d'un scénario
# ---------------------------------------------------------------------------

def _extract_validator_names(ci: ClassInfo) -> list[str]:
    """[FIX-3] Extrait les noms de validators depuis ClassInfo.validators de
    façon défensive -- l'attribut est une liste de ValidatorInfo dont le
    champ peut s'appeler 'name' ou 'method_name' selon la version du reader.
    """
    names: list[str] = []
    for v in (ci.validators or []):
        # Essayer les deux attributs possibles, puis repr() en dernier recours
        name = getattr(v, "name", None) or getattr(v, "method_name", None)
        if name:
            names.append(name)
        else:
            names.append(repr(v))
    return names or ["(aucun validator)"]


def process_one_cross_scenario(
    plan: CrossScenarioPlan,
    class_lookup: dict[str, ClassInfo],
    llm,
    flync_src_root: Path,
    output_dir: Path,
    llm_max_retries: int,
    timeout_seconds: int,
    known_modules: Optional[set[str]] = None,
) -> ScenarioProcessingResult:
    scenario = plan.scenario
    verdict = plan.verdict
    matched_classes = resolve_matched_classes(
        plan.matched_names, class_lookup, scenario["id"], AGENT_LABEL
    )
    bridge_names = set(plan.matched_names) - set(verdict.entities_found_in_model)

    # [FIX-3] Utilise _extract_validator_names() au lieu d'accès direct à .method_name
    validators_by_class: dict[str, list[str]] = {
        ci.name: _extract_validator_names(ci)
        for ci in matched_classes
    }
    exec_success: Optional[bool]

    if plan.category == "requires_sdk":
        content = (
            "import sys\n\n"
            'print("ERROR: scenario requires SDK, out of current KB scope")\n'
            "sys.exit(1)\n"
        )
        exec_success = None

    elif plan.category == "unresolved" or not matched_classes:
        content = (
            "import sys\n\n"
            'print("ERROR: no matching FLYNC class resolved for this '
            'cross-module scenario, even after bridge-class injection")\n'
            "sys.exit(1)\n"
        )
        exec_success = None

    else:
        try:
            content = generate_llm_script_cross(
                scenario, matched_classes, bridge_names,
                validators_by_class, class_lookup, llm,
                flync_src_root, verdict.submodels_declared, plan.bridge_reason,
                max_retries=llm_max_retries,
                resolved_via_rag=verdict.resolved_via_rag,
                timeout_seconds=timeout_seconds,
                known_modules=known_modules,
            )
            exec_success = True

        except LLMGenerationError as exc:
            print(f"[{AGENT_LABEL}] {exc}")
            # Pas de repli gabarit pour le cross-module : script d'échec explicite
            content = (
                "import sys\n\n"
                f'print("ECHEC LLM: {str(exc)[:200]}")\n'
                'print("Aucun repli gabarit -- relecture manuelle requise.")\n'
                "sys.exit(1)\n"
            )
            exec_success = False

    out_path = output_path_for(
        plan.category, scenario["id"], scenario.get("type", "unknown"), output_dir
    )
    out_path.write_text(content, encoding="utf-8")

    return ScenarioProcessingResult(
        scenario_id=scenario["id"],
        agent="cross",
        category=plan.category,
        n_matched_classes=len(matched_classes),
        out_path=out_path,
        execution_success=exec_success,
    )


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def run_cross_agent(
    scenarios: list[dict],
    ctx: SharedContext,
    llm,
    output_dir: Path,
    llm_max_retries: int = DEFAULT_CROSS_MAX_RETRIES,
    max_workers: int = 4,
    timeout_seconds: int = DEFAULT_CROSS_TIMEOUT_SECONDS,
) -> list[ScenarioProcessingResult]:
    if llm is None:
        raise RuntimeError(
            f"[{AGENT_LABEL}] Aucun LLM fourni -- impossible de démarrer : "
            f"cet agent n'a aucun repli gabarit."
        )

    print(
        f"[{AGENT_LABEL}] Classification de {len(scenarios)} scénario(s) "
        f"cross-module (0 appel LLM)..."
    )
    plans = [
        classify_cross_scenario(
            s, ctx.kb_index, ctx.class_lookup, ctx.relation_graph, ctx.retriever
        )
        for s in scenarios
    ]
    _print_classification_report(plans)

    results: list[ScenarioProcessingResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_plan = {
            executor.submit(
                process_one_cross_scenario, plan, ctx.class_lookup, llm,
                ctx.flync_src_root, output_dir, llm_max_retries, timeout_seconds,
                known_modules=ctx.known_modules,
            ): plan
            for plan in plans
        }
        for future in concurrent.futures.as_completed(future_to_plan):
            plan = future_to_plan[future]
            try:
                result = future.result()
                results.append(result)
                status = (
                    "N/A" if result.execution_success is None else
                    "OK" if result.execution_success else "ÉCHEC EXÉCUTION"
                )
                print(
                    f"[{AGENT_LABEL}] {result.scenario_id} "
                    f"({plan.category}, {result.n_matched_classes} classe(s), "
                    f"exécution={status}) -> {result.out_path}"
                )
            except Exception as exc:
                sid = plan.scenario["id"]
                print(f"[{AGENT_LABEL}] ERREUR CRITIQUE sur {sid}: {exc}")
                results.append(ScenarioProcessingResult(
                    scenario_id=sid, agent="cross", category="error",
                    n_matched_classes=0, out_path=None,
                    execution_success=False, error=str(exc),
                ))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Agent Développeur Cross-Module (LLM uniquement)."
    )
    parser.add_argument(
        "--scenarios", required=True,
        help="Fichier JSON des scénarios cross-module UNIQUEMENT.",
    )
    parser.add_argument(
        "--llm-backend", choices=["ollama", "anthropic", "gemini", "groq"], default=None,
    )
    parser.add_argument("--llm-max-retries", type=int, default=DEFAULT_CROSS_MAX_RETRIES)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_CROSS_TIMEOUT_SECONDS)
    parser.add_argument("--output-dir", default="./generated_scripts")
    parser.add_argument("--max-workers", type=int, default=4)

    # [FIX-1] --mode accepté mais ignoré pour compatibilité CLI avec le mono-module.
    # Le cross-module est toujours LLM -- pas de template path.
    parser.add_argument(
        "--mode", choices=["template", "llm"], default="llm",
        help="Ignoré : le cross-module est toujours LLM. "
             "Accepté pour compatibilité avec les scripts qui passent --mode llm.",
    )

    args = parser.parse_args()

    scenarios = load_scenarios(args.scenarios)
    ctx = build_shared_context()
    llm = get_llm(args.llm_backend, category="CROSS_MODULE")  # obligatoire

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    results = run_cross_agent(
        scenarios, ctx, llm, output_dir,
        args.llm_max_retries, args.max_workers, args.timeout_seconds,
    )

    n_ok = sum(1 for r in results if r.execution_success is True)
    n_fail = sum(1 for r in results if r.execution_success is False)
    n_na = sum(1 for r in results if r.execution_success is None)
    print(f"\n[{AGENT_LABEL}] Terminé. {len(results)} scénario(s) -> {output_dir}")
    print(f"[{AGENT_LABEL}] Exécution réelle : {n_ok} OK, {n_fail} échec(s), {n_na} N/A.")

    fail_ids = sorted(r.scenario_id for r in results if r.execution_success is False)
    na_ids = sorted(r.scenario_id for r in results if r.execution_success is None)
    if fail_ids:
        print(f"[{AGENT_LABEL}]   ÉCHEC : {', '.join(fail_ids)}")
    if na_ids:
        print(f"[{AGENT_LABEL}]   N/A   : {', '.join(na_ids)}")

    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
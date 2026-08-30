#!/usr/bin/env python3
"""
agent_developpeur_cross.py
=============================
Agent Développeur Cross-Module.

Traite EXCLUSIVEMENT des scénarios KPIT déclarant 2+ sous-modèles FLYNC
(fichier scenarios-cross.json, séparé en amont du fichier mono-module).

DIFFÉRENCES STRUCTURELLES avec l'Agent Développeur Mono-Module (pas de
simple `if`, l'agent n'a même pas le code pour faire autrement) :

  1. AUCUNE fonction de génération par gabarit n'existe dans ce fichier.
     L'ancien mode template, appliqué au cross-module, produisait des
     scripts syntaxiquement valides mais incapables de modéliser une
     relation entre objets (le rapport de classification de l'ancien
     agent_developpeur.py l'admettait lui-même). Plutôt que d'interdire
     cela par un `if mode == ...`, la capacité est simplement absente ici :
     impossible de l'utiliser par erreur.

  2. Le paramètre `llm` du constructeur/des fonctions est OBLIGATOIRE, pas
     optionnel : si aucun backend LLM n'est configurable, l'agent refuse de
     démarrer plutôt que d'échouer silencieusement plus tard.

  3. Les classes-pont (`ModuleRelationGraph.bridge_class_index`, calculées
     par module_relations.py mais jamais consommées par l'ancien pipeline
     au-delà d'un `print()`) sont injectées de force dans les classes
     transmises au LLM, en complément du matching par nom du Vérificateur
     -- qui rate systématiquement les noms de classes courts (< 4
     caractères, ex: "App", "ECU") et les cas de casse/format différents
     entre le nom de classe (PascalCase, ex: "AppBindings") et le texte du
     scénario (souvent en langage naturel ou en snake_case, ex: "app
     bindings").

  4. Le prompt système explique explicitement les deux mécanismes de
     relation cross-module rencontrés dans le vrai dépôt FLYNC : une
     relation typée (un champ Pydantic référence directement une autre
     classe) et une relation TEXTUELLE (un champ `List[str]` annoté
     `Reference(...)`, résolu manuellement par une méthode dédiée appelée
     depuis un `@model_validator` de la classe agrégat -- jamais un
     validator Pydantic standard sur la classe elle-même). Sans cette
     explication, un LLM qui ne voit qu'un type `List[str]` n'a aucun
     moyen de deviner qu'il s'agit d'une référence croisée vers le champ
     `name` d'une autre classe.

  5. Si la génération LLM échoue après retries, AUCUN repli vers un
     gabarit n'est tenté (il n'existe pas) : un script d'échec explicite
     est écrit, marqué pour relecture manuelle obligatoire.

PATCHES APPLIQUÉS (v5) -- même correctif que agent_developpeur_mono.py,
appliqué ici pour la même raison (cf. commun.py [FIX-7]/[FIX-8]) :
  [FIX-10c] generate_llm_script_cross : ajout de valider_fidelite_valeurs()
            dans la boucle de validation/retry. Le cross-module est encore
            plus exposé à ce risque que le mono, car le LLM y construit
            plusieurs objets liés -- une valeur numérique/textuelle du
            scénario peut facilement finir sur le mauvais objet, ou
            n'apparaître nulle part, sans qu'aucun garde-fou existant ne
            le détecte.
"""

from __future__ import annotations

import argparse
import concurrent.futures
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from flync_pipeline.etape2_lecteur.agent_lecteur_analyste import ClassInfo, FieldInfo
from flync_pipeline.etape2_lecteur.module_relations import ModuleRelationGraph
from flync_pipeline.etape3_verificateur.scenario_verifier import verify_scenario, ScenarioVerdict

from .commun import (
    LLMGenerationError,
    ScenarioProcessingResult,
    SharedContext,
    build_shared_context,
    classes_potentiellement_necessaires,
    execute_generated_script,
    extraire_code_python,
    format_execution_error,
    get_llm,
    load_scenarios,
    output_path_for,
    resolve_matched_classes,
    valider_classes_autorisees,
    valider_contrat_negative,
    valider_syntaxe,
    valider_fidelite_valeurs,   # [FIX-10c]
    extract_scenario_values,
)

AGENT_LABEL = "agent-dev-cross"

# Cette voie fait toujours des appels LLM avec potentiellement plusieurs
# objets imbriqués (App + Controller + FLYNCModel, etc.) -- plus lourd que
# le mono, d'où des valeurs par défaut plus généreuses.
DEFAULT_CROSS_TIMEOUT_SECONDS = 45
DEFAULT_CROSS_MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Enrichissement du verdict : injection des classes-pont
# ---------------------------------------------------------------------------

def _bridge_context_for(
    submodels: list[str],
    relation_graph: ModuleRelationGraph,
    class_lookup: dict[str, ClassInfo],
) -> tuple[set[str], str]:
    """
    Retourne (a) l'ensemble des classes-pont réelles entre les sous-modules
    déclarés par le scénario, et (b) un texte expliquant CE couplage (ou son
    absence) -- à afficher tel quel dans le prompt LLM, pour que celui-ci
    ne suppose jamais une relation qui n'existe pas réellement dans le code.
    """
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
    reason_text = "\n".join(reasons) if reasons else "(aucun couplage AST réel trouvé entre ces sous-modèles)"
    return bridges, reason_text


@dataclass
class CrossScenarioPlan:
    scenario: dict
    verdict: ScenarioVerdict
    matched_names: list[str]      # entités du Vérificateur + classes-pont forcées
    bridge_reason: str
    category: str                 # "cross_module" | "requires_sdk" | "unresolved"


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
        print(f"[{AGENT_LABEL}] INCOHÉRENCE: {scenario['id']} vient du fichier cross-module mais "
              f"submodel='{scenario['submodel']}' ne déclare qu'un seul sous-modèle. "
              f"Traité quand même via cette voie -- à corriger côté fichier KPIT source.")

    bridges, bridge_reason = _bridge_context_for(submodels, relation_graph, class_lookup)
    matched_names = sorted(set(verdict.entities_found_in_model) | bridges)

    if verdict.classification == "REQUIRES_SDK":
        category = "requires_sdk"
    elif not matched_names:
        category = "unresolved"
    else:
        # Un scénario classifié UNRESOLVED par le Vérificateur (aucun match
        # exact/RAG) devient résolu ici si les classes-pont ont comblé le
        # trou -- c'est tout l'intérêt de l'injection forcée.
        category = "cross_module"

    return CrossScenarioPlan(
        scenario=scenario, verdict=verdict, matched_names=matched_names,
        bridge_reason=bridge_reason, category=category,
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
# Génération LLM (cross) -- prompt système spécifique
# ------------------------- --------------------------------------------------

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
    "MÉCANISMES DE RELATION CROSS-MODULE RÉELS DANS FLYNC (les deux existent, "
    "identifie lequel s'applique à partir des champs listés plus bas) :\n"
    "A) RÉFÉRENCE TYPÉE : un champ d'une classe a directement pour type une "
    "autre classe (ou List[AutreClasse]) -- Pydantic valide la structure "
    "automatiquement à la construction.\n"
    "B) RÉFÉRENCE TEXTUELLE (fréquente entre sous-modules) : un champ "
    "`List[str]` (ou `str`) porte un NOM qui doit correspondre au champ "
    "`name` d'un objet défini ailleurs dans le modèle. Cette correspondance "
    "n'est PAS vérifiée par Pydantic à la construction de l'objet isolé : "
    "elle est résolue par une méthode dédiée ou un `@model_validator` sur "
    "une classe AGRÉGAT de plus haut niveau (souvent le modèle racine), qui "
    "parcourt tous les objets du système. CONSÉQUENCE PRATIQUE : si le champ "
    "fourni ci-dessous est un simple `List[str]`/`str` (pas un type de "
    "classe), tu dois construire l'agrégat qui contient et résout cette "
    "référence -- pas seulement l'objet qui porte le champ -- et entourer "
    "la construction de CET AGRÉGAT (pas de l'objet feuille) par le "
    "try/except attendu si le scénario est Negative.\n\n"
    "RÈGLES DE CONTENU :\n"
    "1. CE N'EST PAS UN TEST : jamais pytest, jamais assert, jamais "
    "pytest.raises, jamais de fonction test_*().\n"
    "2. Instancie TOUTES les classes explicitement fournies ci-dessous "
    "(y compris les classes-pont marquées [PONT]), avec un import par "
    "classe -- même celles qui ne sont pas nommées littéralement dans le "
    "texte du scénario mais qui matérialisent la relation entre les "
    "sous-modules concernés.\n"
    "3. Chaque valeur de champ doit être concrète et plausible. Utilise la "
    "valeur EXACTE du scénario quand elle est donnée -- voir le bloc "
    "VALEURS DU SCÉNARIO ci-dessous, qui sera vérifié automatiquement après "
    "génération. Pour une référence textuelle (mécanisme B ci-dessus), "
    "utilise des noms COHÉRENTS entre les deux côtés de la relation pour un "
    "scénario Positive (même chaîne des deux côtés), et un nom "
    "délibérément absent/différent pour reproduire une référence pendante "
    "(dangling) dans un scénario Negative.\n"
    "4. N'invente JAMAIS un champ, une classe ou un validator non listés.\n"
    "4bis. N'IMPORTE PAS puis REDÉFINIS une classe FLYNC.\n"
    "4ter. Si une classe listée est marquée [ENUM], ne l'instancie JAMAIS "
    "avec des parenthèses : référence un de ses membres.\n\n"
    "COUPLAGE RÉEL ENTRE LES SOUS-MODÈLES DÉCLARÉS :\n"
    "5. Le texte 'Couplage AST réel détecté' fourni plus bas dans le prompt "
    "humain fait foi. S'il indique qu'AUCUN couplage réel n'a été trouvé, "
    "construis les objets de chaque sous-modèle INDÉPENDAMMENT -- n'invente "
    "aucune référence, aucun champ de liaison, aucune classe intermédiaire "
    "pour simuler une relation qui n'existe pas dans le vrai code.\n"
    "6. S'il indique un couplage réel (avec la classe-pont concernée), "
    "cette classe DOIT apparaître dans ta construction, portant la "
    "référence (typée ou textuelle) décrite en A/B ci-dessus.\n\n"
    "CONTRAT D'EXIT CODE, STRICT ET SANS EXCEPTION :\n"
    "- `import sys` est TOUJOURS la toute première ligne du script.\n"
    "- Positive : instanciation réelle de TOUS les objets nécessaires "
    "(y compris l'agrégat si le mécanisme est textuel, cf. ci-dessus), SANS "
    "try/except, puis print(\"SUCCESS\") puis sys.exit(0).\n"
    "- Negative : `from pydantic import ValidationError`, puis TOUTE la "
    "construction (tous les objets requis par la relation) dans un seul "
    "bloc try/except/else autour de la construction de l'AGRÉGAT le plus "
    "englobant nécessaire pour que la validation ait lieu, sys.exit(0) si "
    "la ValidationError attendue est levée, sys.exit(1) sinon.\n\n"
    "GARDE-FOUS (aucune exception) :\n"
    "7. VALIDATION DISPONIBLE UNIQUEMENT : ne suppose jamais qu'une "
    "ValidationError sera levée si aucun mécanisme réel (champ, validator, "
    "méthode de résolution) fourni ci-dessous ne le permet.\n"
    "8. AUCUNE SIMULATION : pas de classe locale, Meta, validator custom, "
    "registre ou dictionnaire pour imiter un mécanisme absent des classes "
    "fournies. Uniquement les modèles réels importés du package FLYNC.\n"
    "9. FAUTES GLOBALES : si la faute nécessite plusieurs objets, "
    "construis-les TOUS. Ne suppose jamais qu'une instanciation isolée "
    "suffit pour une contrainte qui vit sur un agrégat.\n\n"
    "VALIDATION RÉELLE :\n"
    "10. Ce script est ENSUITE RÉELLEMENT EXÉCUTÉ (subprocess isolé) avant "
    "d'être accepté. Un échec (NameError, ImportError, AttributeError, "
    "TypeError, ValidationError inattendue...) te renvoie le traceback réel "
    "à corriger -- il n'y a AUCUN repli automatique vers autre chose si tu "
    "épuises tes tentatives : le scénario restera en échec et sera relu "
    "manuellement. Le script est également vérifié pour fidélité aux "
    "valeurs listées dans VALEURS DU SCÉNARIO.\n"
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
    blocks = []
    import_lines = []
    for ci in matched_classes:
        all_fields = _resolve_all_fields(ci, class_lookup)
        field_lines = []
        for f in all_fields:
            constraint = f" | contrainte réelle: {f.default_str}" if f.default_str and "Field(" in (f.default_str or "") else ""
            referenced = class_lookup.get(f.type_str.strip())
            type_note = ""
            if referenced is not None and referenced.is_enum:
                type_note = f" | [ENUM, membres: {', '.join(referenced.enum_members) or 'aucun détecté'}]"
            elif f.type_str.strip().startswith(("List[str]", "list[str]", "str")):
                type_note = " | [RÉFÉRENCE TEXTUELLE POSSIBLE -- lis 'mécanisme B' du prompt système]"
            field_lines.append(f"  - {f.name}: {f.type_str} | obligatoire={f.required}{constraint}{type_note}")
        class_validators = [v for v in validators_by_class.get(ci.name, []) if v != "(aucun validator)"]
        notes = []
        if ci.name in bridge_names:
            notes.append("[PONT: cette classe matérialise le couplage réel entre les sous-modules déclarés]")
        if ci.name in resolved_via_rag:
            notes.append("[NOTE: résolue par similarité sémantique (RAG), confiance modérée]")
        note_str = ("\n" + " ".join(notes)) if notes else ""
        blocks.append(
            f"{ci.name} (module réel: {ci.module}, fichier: {ci.file}){note_str}\n"
            f"Champs (avec héritage résolu) :\n" + "\n".join(field_lines) + "\n"
            f"Validators réels sur cette classe : {class_validators or '(aucun)'}"
        )
        module_file_stem = ci.file.removesuffix(".py")
        import_lines.append(f"from flync.model.{ci.module}.{module_file_stem} import {ci.name}")

    classes_desc = "\n\n".join(blocks) if blocks else "aucune classe résolue, même après injection des classes-pont"
    imports_hint = "\n".join(import_lines) if import_lines else "# aucun import déterminable automatiquement"

    scenario_values = extract_scenario_values(scenario)
    from .commun import format_scenario_values_block
    values_block = format_scenario_values_block(scenario_values)

    human = (
        f"Scénario : {scenario['id']} ({scenario['type']})\n"
        f"Sous-modèles déclarés : {', '.join(submodels)}\n"
        f"Titre : {scenario['title']}\n"
        f"Description : {scenario['description']}\n"
        f"Fault injecté : {scenario.get('injected_fault')}\n"
        f"Résultat attendu : {scenario['expected_result']}\n\n"
        f"Couplage AST réel détecté entre ces sous-modèles :\n{bridge_reason}\n\n"
        f"Imports réels à utiliser :\n{imports_hint}\n\n"
        f"Classe(s) disponible(s) ({len(matched_classes)}) :\n{classes_desc}\n\n"
        f"{values_block}\n\n"
        f"Rappel : réponds UNIQUEMENT avec un bloc ```python contenant le "
        f"script complet, sans aucun texte avant/après, sans commentaire, "
        f"en commençant par `import sys`."
    )
    if feedback:
        human += f"\n\nFEEDBACK D'UNE EXÉCUTION PRÉCÉDENTE (corrige le script généré) :\n{feedback}"
    return human


def _resolve_all_fields(class_info: ClassInfo, class_lookup: dict[str, ClassInfo]) -> list[FieldInfo]:
    seen_names: set[str] = set()
    all_fields: list[FieldInfo] = []

    def _walk(ci: ClassInfo) -> None:
        for base_name in ci.bases:
            base_info = class_lookup.get(base_name)
            if base_info is not None:
                _walk(base_info)
        for f in ci.fields:
            if f.name not in seen_names:
                seen_names.add(f.name)
                all_fields.append(f)

    _walk(class_info)
    return all_fields


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
) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    human_prompt = _construire_prompt_humain_cross(
        scenario, matched_classes, bridge_names, validators_by_class, class_lookup,
        submodels, bridge_reason, feedback, resolved_via_rag,
    )
    messages = [SystemMessage(content=_SYSTEM_PROMPT_LLM_CROSS), HumanMessage(content=human_prompt)]
    allowed_names = classes_potentiellement_necessaires(matched_classes, class_lookup)

    # [FIX-10c] Valeurs du scénario + champs réels connus (toutes classes,
    # y compris les classes-pont) pour la vérification de fidélité.
    scenario_values = extract_scenario_values(scenario)
    known_field_names: set[str] = set()
    for ci in matched_classes:
        known_field_names |= {f.name for f in _resolve_all_fields(ci, class_lookup)}

    attempt_errors: list[tuple[int, str, str]] = []
    for attempt in range(1, max_retries + 2):
        response = llm.invoke(messages)
        code = extraire_code_python(response.content)

        error = valider_syntaxe(code)
        error_kind = "syntaxe"
        if error is None:
            error = valider_classes_autorisees(code, allowed_names)
            error_kind = "classes hors périmètre / shadowing"
        if error is None and scenario.get("type") == "Negative":
            error = valider_contrat_negative(code)
            error_kind = "contrat exit-code Negative violé"
        if error is None:
            exec_result = execute_generated_script(code, flync_src_root, timeout_seconds=timeout_seconds)
            if not exec_result.success:
                error = format_execution_error(exec_result)
                error_kind = "exécution réelle"
        if error is None:
            # [FIX-10c] Même logique que le mono : une exécution réussie ne
            # garantit pas que les valeurs demandées ont été utilisées,
            # d'autant plus risqué ici avec plusieurs objets liés où une
            # valeur peut se retrouver sur le mauvais objet sans provoquer
            # d'erreur d'exécution.
            error = valider_fidelite_valeurs(code, scenario_values, known_field_names)
            error_kind = "valeurs du scénario non respectées"
        if error is None:
            return code
        attempt_errors.append((attempt, error_kind, error))
        print(f"[{AGENT_LABEL}] {scenario['id']}: {error_kind} invalide (tentative {attempt}) -> {error}")

        last_error = error
        print(f"[{AGENT_LABEL}] {scenario['id']}: {error_kind} invalide (tentative {attempt}) -> {error}")
        messages.append(response)
        messages.append(HumanMessage(content=(
            f"Le code précédent est rejeté ({error_kind}) : {error}\n"
            f"Renvoie UNIQUEMENT le code Python corrigé, sous forme d'un unique "
            f"bloc ```python, en commençant par `import sys`, sans aucun texte "
            f"hors du code, sans commentaire. Rappel : aucun repli n'existe pour "
            f"ce scénario cross-module -- corrige le mécanisme de relation si "
            f"c'est la cause de l'échec, ne le supprime pas."
        )))

    kinds_seen = [k for _, k, _ in attempt_errors]
    repeated = len(set(kinds_seen)) == 1 and len(kinds_seen) > 1
    history = "\n".join(f"  tentative {a}: [{k}] {m}" for a, k, m in attempt_errors)
    suffix = " (même type d'erreur à chaque tentative -- hallucination probablement stable)" if repeated else ""
    raise LLMGenerationError(
        f"{scenario['id']}: échec de génération LLM après {max_retries + 1} tentative(s){suffix}.\n{history}"
    )

# ---------------------------------------------------------------------------
# Traitement d'un scénario (unité de parallélisation)
# ---------------------------------------------------------------------------

def process_one_cross_scenario(
    plan: CrossScenarioPlan,
    class_lookup: dict[str, ClassInfo],
    llm,
    flync_src_root: Path,
    output_dir: Path,
    llm_max_retries: int,
    timeout_seconds: int,
) -> ScenarioProcessingResult:
    scenario = plan.scenario
    verdict = plan.verdict
    matched_classes = resolve_matched_classes(plan.matched_names, class_lookup, scenario["id"], AGENT_LABEL)
    bridge_names = set(plan.matched_names) - set(verdict.entities_found_in_model)
    validators_by_class = {
        ci.name: ([v.method_name for v in ci.validators] or ["(aucun validator)"])
        for ci in matched_classes
    }

    if plan.category == "requires_sdk":
        content = (
            "import sys\n\n"
            'print("ERROR: scenario requires SDK, out of current KB scope")\n'
            "sys.exit(1)\n"
        )
        exec_success: Optional[bool] = None
    elif plan.category == "unresolved" or not matched_classes:
        content = (
            "import sys\n\n"
            'print("ERROR: no matching FLYNC class resolved for this cross-module scenario, '
            'even after bridge-class injection")\n'
            "sys.exit(1)\n"
        )
        exec_success = None
    else:
        try:
            content = generate_llm_script_cross(
                scenario, matched_classes, bridge_names, validators_by_class, class_lookup, llm,
                flync_src_root, verdict.submodels_declared, plan.bridge_reason,
                max_retries=llm_max_retries, resolved_via_rag=verdict.resolved_via_rag,
                timeout_seconds=timeout_seconds,
            )
            exec_success = True
        except LLMGenerationError as exc:
            print(f"[{AGENT_LABEL}] {exc}")
            content = (
                "import sys\n\n"
                f'print("ECHEC DE GENERATION LLM APRES RETRIES: {exc}")\n'
                'print("Aucun repli gabarit pour un scenario cross-module -- relecture manuelle requise.")\n'
                "sys.exit(1)\n"
            )
            exec_success = False

    out_path = output_path_for(plan.category, scenario["id"], scenario.get("type", "unknown"), output_dir)
    out_path.write_text(content, encoding="utf-8")

    return ScenarioProcessingResult(
        scenario_id=scenario["id"], agent="cross", category=plan.category,
        n_matched_classes=len(matched_classes), out_path=out_path, execution_success=exec_success,
    )


# ---------------------------------------------------------------------------
# Point d'entrée de l'agent
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
            f"[{AGENT_LABEL}] Aucun LLM fourni -- impossible de démarrer : cet agent n'a aucun "
            f"repli gabarit, contrairement à l'Agent Développeur Mono-Module."
        )

    print(f"[{AGENT_LABEL}] Classification de {len(scenarios)} scénario(s) cross-module (0 appel LLM)...")
    plans = [
        classify_cross_scenario(s, ctx.kb_index, ctx.class_lookup, ctx.relation_graph, ctx.retriever)
        for s in scenarios
    ]
    _print_classification_report(plans)

    results: list[ScenarioProcessingResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_plan = {
            executor.submit(
                process_one_cross_scenario, plan, ctx.class_lookup, llm,
                ctx.flync_src_root, output_dir, llm_max_retries, timeout_seconds,
            ): plan
            for plan in plans
        }
        for future in concurrent.futures.as_completed(future_to_plan):
            plan = future_to_plan[future]
            try:
                result = future.result()
                results.append(result)
                status = "N/A" if result.execution_success is None else ("OK" if result.execution_success else "ÉCHEC EXÉCUTION")
                print(f"[{AGENT_LABEL}] {result.scenario_id} ({plan.category}, {result.n_matched_classes} classe(s), "
                      f"exécution={status}) -> {result.out_path}")
            except Exception as exc:
                sid = plan.scenario["id"]
                print(f"[{AGENT_LABEL}] ERREUR CRITIQUE sur {sid}: {exc}")
                results.append(ScenarioProcessingResult(
                    scenario_id=sid, agent="cross", category="error",
                    n_matched_classes=0, out_path=None, execution_success=False, error=str(exc),
                ))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Développeur Cross-Module (LLM uniquement).")
    parser.add_argument("--scenarios", required=True, help="Fichier JSON des scénarios cross-module UNIQUEMENT.")
    parser.add_argument("--llm-backend", choices=["ollama", "anthropic", "gemini"], default=None)
    parser.add_argument("--llm-max-retries", type=int, default=DEFAULT_CROSS_MAX_RETRIES)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_CROSS_TIMEOUT_SECONDS)
    parser.add_argument("--output-dir", default="./generated_scripts")
    parser.add_argument("--max-workers", type=int, default=4)
    args = parser.parse_args()
    # Pas de --mode : il n'y a qu'un seul mode possible pour cet agent.

    scenarios = load_scenarios(args.scenarios)
    ctx = build_shared_context()
    llm = get_llm(args.llm_backend)  # obligatoire, pas de branche "None"

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    results = run_cross_agent(
        scenarios, ctx, llm, output_dir, args.llm_max_retries, args.max_workers, args.timeout_seconds,
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

    # [NOUVEAU] rapport de couverture formel -- voir coverage_report.py
    from flync_pipeline.etape4_developpeur import (
        build_coverage_report, render_markdown, render_mermaid_pie,
    )
    scenarios_by_id = {s["id"]: s for s in scenarios}
    cov = build_coverage_report(results, scenarios_by_id)
    (output_dir / "coverage_report.md").write_text(render_markdown(cov), encoding="utf-8")
    (output_dir / "coverage_pie.mmd").write_text(render_mermaid_pie(cov), encoding="utf-8")
    print(f"[{AGENT_LABEL}] Rapport de couverture -> {output_dir / 'coverage_report.md'}")

    return 0 if n_fail == 0 else 2

if __name__ == "__main__":
    raise SystemExit(main())
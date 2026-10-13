
from __future__ import annotations

import argparse
import concurrent.futures
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from phase2.src.flync_pipeline.etape2_lecteur.agent_lecteur_analyste import ClassInfo, FieldInfo
from phase2.src.flync_pipeline.etape3_verificateur.scenario_verifier import verify_scenario, ScenarioVerdict

from .commun import (
    DEFAULT_EXECUTION_TIMEOUT_SECONDS,
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
    valider_imports_flync,
    valider_fidelite_valeurs,       # [FIX-10]
    check_orphan_scenario_values,   # [FIX-11]
    extract_scenario_values,
    is_scenario_isolation_impossible,
    format_scenario_values_block,
)

AGENT_LABEL = "agent-dev-mono"



def _extract_annotated_inner_type(t: str) -> Optional[str]:
    """Extrait le premier argument de type d'un `Annotated[X, ...]`, en
    respectant la profondeur des crochets -- contrairement à l'ancienne regex
    qui coupait sur la première virgule rencontrée, y compris à l'intérieur
    d'un générique imbriqué comme Dict[str, int].

    Retourne une chaîne (le type extrait) ou None si `t` ne commence pas par
    "Annotated[". NE retourne PAS un objet re.Match -- tout appelant doit
    utiliser la valeur directement, jamais via .group(...)."""
    prefix = "Annotated["
    if not t.startswith(prefix):
        return None
    depth = 0
    for i, ch in enumerate(t[len(prefix):], start=len(prefix)):
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        elif ch == "," and depth == 0:
            return t[len(prefix):i].strip()
    return None


_MAX_NESTED_DEPTH = 3


def infer_placeholder(
    field_info: FieldInfo,
    class_lookup: dict[str, ClassInfo],
    _depth: int = 0,
    _visited: Optional[frozenset[str]] = None,
    _referenced_classes: Optional[set[str]] = None,
    scenario_values: Optional[dict[str, any]] = None,
) -> tuple[str, bool]:
    scenario_values = scenario_values or {}

    if field_info.name in scenario_values:
        raw_val = scenario_values[field_info.name]
        t = field_info.type_str.strip()

        if t == "str" or t.startswith("Optional[str]"):
            return f'"{raw_val}"', True
        if t == "int" or t.startswith("Optional[int]"):
            try:
                return str(int(raw_val)), True
            except (ValueError, TypeError):
                pass
        if t == "float" or t.startswith("Optional[float]"):
            try:
                return str(float(raw_val)), True
            except (ValueError, TypeError):
                pass
        if t == "bool" or t.startswith("Optional[bool]"):
            if isinstance(raw_val, bool):
                return str(raw_val), True
            if isinstance(raw_val, str):
                return str(raw_val.lower() == "true"), True
        if t.startswith("Literal["):
            inner = t[len("Literal["):-1]
            options = [opt.strip().strip("\'\"") for opt in inner.split(",")]
            val_str = str(raw_val)
            if val_str in options:
                return val_str, True
            return options[0] if options else f'"{raw_val}"', False
        return f'"{raw_val}"' if isinstance(raw_val, str) else str(raw_val), True

    if _visited is None:
        _visited = frozenset()
    t = field_info.type_str.strip()

    inner_type = _extract_annotated_inner_type(t)
    if inner_type:
        inner_field = FieldInfo(field_info.name, inner_type, field_info.required, field_info.default_str)
        return infer_placeholder(inner_field, class_lookup, _depth, _visited, _referenced_classes, scenario_values)

    if t.startswith("Literal["):
        inner = t[len("Literal["):-1]
        return inner.split(",")[0].strip(), True
    if t.startswith("Optional["):
        return "None", True
    if t.startswith("List[") or t.startswith("list["):
        return "[]", True
    if t == "str":
        return f'"demo_{field_info.name}"', True
    if t == "int":
        return "1", True
    if t == "float":
        return "1.0", True
    if t == "bool":
        return "False", True

    referenced = class_lookup.get(t)
    if referenced is not None and t not in _visited and _depth < _MAX_NESTED_DEPTH:
        if _referenced_classes is not None:
            _referenced_classes.add(referenced.name)

        if referenced.is_enum:
            if referenced.enum_members:
                return f"{referenced.name}.{referenced.enum_members[0]}", True
            return "None", False

        nested_visited = _visited | {t}
        nested_parts: list[str] = []
        all_nested_resolved = True
        for nf in resolve_all_fields(referenced, class_lookup):
            if not nf.required and nf.name not in scenario_values:
                continue
            nv, n_resolved = infer_placeholder(nf, class_lookup, _depth + 1, nested_visited, _referenced_classes, scenario_values)
            all_nested_resolved = all_nested_resolved and n_resolved
            nested_parts.append(f"{nf.name}={nv}")
        return f"{referenced.name}({', '.join(nested_parts)})", all_nested_resolved

    return "None", False


def resolve_all_fields(class_info: ClassInfo, class_lookup: dict[str, ClassInfo]) -> list[FieldInfo]:
    """Résout tous les champs d'une classe en remontant l'héritage (MRO
    simplifié : bases dans l'ordre de déclaration, sans diamond)."""
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


def _var_name_for(class_info: ClassInfo) -> str:
    s = re.sub(r"(?<!^)(?<![A-Z])(?=[A-Z])", "_", class_info.name)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    return s.lower()


def build_construction_snippet(
    class_info: ClassInfo,
    class_lookup: dict[str, ClassInfo],
    indent: str = "",
    referenced_classes: Optional[set[str]] = None,
    scenario_values: Optional[dict[str, any]] = None,
) -> tuple[list[str], list[str]]:
    """[PATCH v4] Accepte scenario_values pour propager les valeurs extraites."""
    var_name = _var_name_for(class_info)
    lines = [f"{indent}{var_name} = {class_info.name}("]
    warnings: list[str] = []
    for f in resolve_all_fields(class_info, class_lookup):
        if not f.required and f.name not in (scenario_values or {}):
            continue
        value, resolved = infer_placeholder(f, class_lookup, _referenced_classes=referenced_classes, scenario_values=scenario_values)
        if not resolved:
            warnings.append(
                f"{class_info.name}.{f.name}: type '{f.type_str}' non résolu "
                f"automatiquement, valeur de repli 'None' utilisée"
            )
        lines.append(f"{indent}    {f.name}={value},")
    lines.append(f"{indent})")
    return lines, warnings


def generate_construction_script(
    scenario: dict,
    matched_classes: list[ClassInfo],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
) -> tuple[str, list[str]]:
    """[PATCH v4] Génération déterministe avec extraction des valeurs du scénario."""
    scenario_id = scenario["id"]
    scenario_type = scenario["type"]
    warnings: list[str] = []

    # [PATCH v4] Extraction des valeurs du scénario
    scenario_values = extract_scenario_values(scenario)
    if scenario_values:
        print(
            f"[{AGENT_LABEL}] {scenario_id}: valeurs extraites du scénario: "
            f"{scenario_values}"
        )

    if not matched_classes:
        content = (
            "import sys\n\n"
            '"ERROR: no matching FLYNC class resolved for this scenario")\n'
            "sys.exit(1)\n"
        )
        return content, [f"{scenario_id}: aucune classe résolue -- script de repli (exit=1) généré"]

    known_field_names: set[str] = set()
    for ci in matched_classes:
        known_field_names |= {f.name for f in resolve_all_fields(ci, class_lookup)}
    orphan_keys = check_orphan_scenario_values(scenario_values, known_field_names)
    if orphan_keys:
        warnings.append(
            f"{scenario_id}: GAP -- le scénario mentionne {', '.join(orphan_keys)}, "
            f"mais aucun champ de ce nom n'existe sur "
            f"{', '.join(ci.name for ci in matched_classes)} "
            f"(champs réels disponibles : {', '.join(sorted(known_field_names)) or '(aucun)'}). "
            f"Le scénario KPIT emploie peut-être un nom différent du schéma réel "
            f"(ex: 'min_interval'/'max_interval' vs. un champ réel 'period') -- "
            f"à vérifier côté Vérificateur/KB, le gabarit ne peut pas deviner "
            f"la correspondance."
        )

    injected_fault = scenario.get("injected_fault")
    if scenario_type == "Negative" and injected_fault:
        warnings.append(
            f"{scenario_id}: Negative -- ajuster manuellement le(s) champ(s) "
            f"pour reproduire : {injected_fault}"
        )
    for ci in matched_classes:
        class_validators = [v for v in validators_by_class.get(ci.name, []) if v != "(aucun validator)"]
        if scenario_type == "Negative" and not class_validators:
            warnings.append(
                f"{scenario_id}: GAP -- {ci.name} n'a aucun validator connu ; la branche "
                f"ValidationError ne sera probablement pas atteinte via cette classe."
            )

    indent = "    " if scenario_type == "Negative" else ""
    all_construction_lines: list[str] = []
    referenced_classes: set[str] = set()
    for ci in matched_classes:
        lines, field_warnings = build_construction_snippet(
            ci, class_lookup, indent=indent, referenced_classes=referenced_classes,
            scenario_values=scenario_values,
        )

        warnings.extend(f"{scenario_id}: {w}" for w in field_warnings)
        all_construction_lines.extend(lines)
    construction_block = "\n".join(all_construction_lines)

    already_imported = {ci.name for ci in matched_classes}
    extra_classes = [
        class_lookup[name] for name in sorted(referenced_classes)
        if name not in already_imported and name in class_lookup
    ]
    import_lines = []
    for ci in [*matched_classes, *extra_classes]:
        module_file_stem = ci.file.removesuffix(".py")
        import_lines.append(f"from flync.model.{ci.module}.{module_file_stem} import {ci.name}")
    imports_block = "\n".join(import_lines)

    if scenario_type == "Positive":
        body = (
            "import sys\n\n"
            f"{imports_block}\n\n"
            f"{construction_block}\n\n"
            'print("SUCCESS")\n'
            "sys.exit(0)\n"
        )
    else:
        body = (
            "import sys\n"
            "from pydantic import ValidationError\n\n"
            f"{imports_block}\n\n"
            "try:\n"
            f"{construction_block}\n"
            "except ValidationError as exc:\n"
            '    print(f"EXPECTED ERROR: {exc}")\n'
            "    sys.exit(0)\n"
            "except Exception as exc:\n"
            '    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")\n'
            "    sys.exit(1)\n"
            "else:\n"
            '    print("ERROR: expected ValidationError but no error was raised")\n'
            "    sys.exit(1)\n"
        )
    return body, warnings



_SYSTEM_PROMPT_LLM_MONO = (
    "Tu es un générateur de code Python pour le framework FLYNC (modèles "
    "Pydantic v2 réels, pas une simulation). Le scénario que tu reçois "
    "concerne UN SEUL sous-modèle FLYNC -- il peut malgré tout impliquer "
    "plusieurs classes liées entre elles au sein de ce même sous-modèle.\n\n"
    "FORMAT DE RÉPONSE, ABSOLU ET NON NÉGOCIABLE :\n"
    "- Ta réponse ENTIÈRE doit être un unique bloc ```python ... ``` et rien "
    "d'autre. Aucune phrase avant, aucune phrase après, aucune explication.\n"
    "- Le code ne doit contenir NI commentaire (#), NI docstring, NI texte "
    "quelconque : uniquement des instructions Python exécutables.\n\n"
    "RÈGLES DE CONTENU :\n"
    "1. CE N'EST PAS UN TEST : n'importe jamais pytest, n'écris jamais assert, "
    "jamais pytest.raises, jamais de fonction test_*().\n"
    "2. Chaque valeur de champ doit être concrète et plausible, jamais un "
    "placeholder générique. Utilise la valeur EXACTE du scénario quand elle "
    "est donnée -- voir le bloc VALEURS DU SCÉNARIO ci-dessous, qui fait "
    "autorité et sera vérifié automatiquement après génération. Pour "
    "Negative, utilise la valeur fautive exacte lorsqu'elle est fournie, ou "
    "construis une valeur qui viole réellement la contrainte identifiée par "
    "le Vérificateur.\n"
    "3. RÈGLE ABSOLUE SUR LES CHAMPS : n'utilise QUE les champs listés dans "
    "le bloc 'CHAMPS AUTORISÉS' fourni dans le prompt utilisateur. "
    "Ne déduis JAMAIS un champ depuis la description du scénario. "
    "Tout champ absent de cette liste est INEXISTANT sur le modèle Pydantic "
    "réel -- l'utiliser provoque extra_forbidden ValidationError et exit(1).\n"
    "4. N'IMPORTE PAS puis REDÉFINIS une classe FLYNC : si tu écris "
    "`from flync.model... import X`, n'écris JAMAIS ensuite `class X(...):`.\n"
    "5. Si une classe listée est marquée [ENUM], ne l'instancie JAMAIS avec "
    "des parenthèses : référence un de ses membres listés.\n"
    "6. Utilise les imports réels donnés, jamais un chemin deviné.\n\n"
    "CONTRAT D'EXIT CODE, STRICT ET SANS EXCEPTION :\n"
    "- `import sys` est TOUJOURS la toute première ligne du script -- ce "
    "script est réellement exécuté, un `import sys` manquant provoque un "
    "NameError immédiat sur `sys.exit(...)`.\n"
    "- Positive : instanciation réelle de TOUS les objets, SANS try/except, "
    "puis print(\"SUCCESS\") puis sys.exit(0). Ne jamais intercepter une "
    "exception imprévue.\n"
    "- Negative : `from pydantic import ValidationError`, puis TOUTE la "
    "construction dans un seul bloc try, sys.exit(0) UNIQUEMENT dans le "
    "except ValidationError (jamais dans le try ni dans le else), "
    "sys.exit(1) dans le else et dans tout autre except.\n\n"
    "RELATIONS ENTRE OBJETS DU MÊME SOUS-MODÈLE :\n"
    "7. Si la description mentionne explicitement une relation entre "
    "plusieurs entités du même sous-modèle, reproduis-la RÉELLEMENT si les "
    "classes/champs fournis le permettent (identifiants ou noms COHÉRENTS "
    "entre les objets liés). N'invente jamais un champ ou une relation qui "
    "n'est pas confirmée par les classes fournies.\n"
    "8. REPRODUCTION EXACTE DE LA FAUTE : pour un scénario Negative, la "
    "construction doit provoquer réellement la faute décrite selon le "
    "mécanisme Pydantic réel identifié -- jamais une ValidationError "
    "imaginaire si aucun mécanisme réel ne la produit.\n"
    "9. INTERDICTION DE MOCKING : aucune classe locale, Meta, validator "
    "custom ou stub. Uniquement les modèles importés du package FLYNC.\n\n"
    "VALIDATION RÉELLE :\n"
    "10. Ce script est ENSUITE RÉELLEMENT EXÉCUTÉ (subprocess isolé) avant "
    "d'être accepté. S'il échoue (NameError, ImportError, AttributeError, "
    "TypeError, ValidationError inattendue...), tu recevras le traceback "
    "réel et devras corriger en conséquence. Le script est également vérifié "
    "pour fidélité : si une valeur listée dans VALEURS DU SCÉNARIO n'apparaît "
    "pas telle quelle dans ton code, il sera rejeté même s'il s'exécute "
    "sans erreur.\n"
)


def _build_field_allowlist_block(
    matched_classes: list[ClassInfo],
    class_lookup: dict[str, ClassInfo],
) -> str:
    """[FIX-A] Construit le bloc textuel 'CHAMPS AUTORISÉS' à injecter dans
    le prompt humain. Liste les champs exacts (avec héritage résolu) de
    chaque classe matchée, pour empêcher le LLM d'halluciner des champs
    mentionnés dans la description du scénario mais absents du modèle."""
    if not matched_classes:
        return "CHAMPS AUTORISÉS : (aucune classe résolue)"
    lines: list[str] = ["CHAMPS AUTORISÉS (liste exhaustive -- aucun autre champ n'existe sur ces classes) :"]
    for ci in matched_classes:
        all_fields = resolve_all_fields(ci, class_lookup)
        if all_fields:
            field_names = ", ".join(f.name for f in all_fields)
        else:
            field_names = "(aucun champ déclaré)"
        lines.append(f"  {ci.name} : {field_names}")
    lines.append(
        "Tout champ absent de ces listes est INEXISTANT sur le modèle Pydantic réel. "
        "L'utiliser provoque une ValidationError extra_forbidden immédiate (exit=1). "
        "Ne jamais se fier à la description du scénario pour déduire des champs."
    )
    return "\n".join(lines)


def _construire_prompt_humain_mono(
    scenario: dict,
    matched_classes: list[ClassInfo],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
    feedback: Optional[str],
    resolved_via_rag: Optional[list[str]] = None,
) -> str:
    resolved_via_rag = resolved_via_rag or []
    if not matched_classes:
        classes_desc = "aucune classe résolue localement"
        imports_hint = "# aucun import déterminable automatiquement"
    else:
        blocks = []
        import_lines = []
        for ci in matched_classes:
            all_fields = resolve_all_fields(ci, class_lookup)
            field_lines = []
            for f in all_fields:
                constraint = (
                    f" | contrainte réelle: {f.default_str}"
                    if f.default_str and "Field(" in (f.default_str or "")
                    else ""
                )
                # [REVUE-1] _extract_annotated_inner_type retourne une chaîne
                # (ou None) -- PAS un objet re.Match. L'ancien `.group(1)`
                # laissé ici plantait sur tout champ Annotated[...].
                inner_type = _extract_annotated_inner_type(f.type_str.strip()) or f.type_str.strip()
                referenced = class_lookup.get(inner_type)
                type_note = ""
                if referenced is not None and referenced.is_enum:
                    type_note = (
                        f" | [ENUM, membres: "
                        f"{', '.join(referenced.enum_members) or 'aucun détecté'}]"
                    )
                field_lines.append(
                    f"  - {f.name}: {f.type_str} | "
                    f"obligatoire={f.required}{constraint}{type_note}"
                )
            class_validators = [
                v for v in validators_by_class.get(ci.name, []) if v != "(aucun validator)"
            ]
            rag_note = (
                "\n[NOTE: classe résolue par similarité sémantique (RAG), pas par mention "
                "exacte de son nom -- confiance modérée, vérifie sa pertinence]"
                if ci.name in resolved_via_rag else ""
            )
            blocks.append(
                f"{ci.name} (module réel: {ci.module}, fichier: {ci.file}){rag_note}\n"
                f"Champs (avec héritage résolu) :\n" + "\n".join(field_lines) + "\n"
                f"Validators réels sur cette classe : "
                f"{class_validators or '(aucun)'}"
            )
            module_file_stem = ci.file.removesuffix(".py")
            import_lines.append(
                f"from flync.model.{ci.module}.{module_file_stem} import {ci.name}"
            )
        classes_desc = "\n\n".join(blocks)
        imports_hint = "\n".join(import_lines)

    # [FIX-A] Bloc de contrainte sur les champs, injecté explicitement
    field_allowlist_block = _build_field_allowlist_block(matched_classes, class_lookup)

    scenario_values = extract_scenario_values(scenario)
    values_block = format_scenario_values_block(scenario_values)

    human = (
            f"Scénario : {scenario['id']} ({scenario['type']})\n"
            f"Titre : {scenario['title']}\n"
            f"Description : {scenario['description']}\n"
            f"Fault injecté : {scenario.get('injected_fault')}\n"
            f"Résultat attendu : {scenario['expected_result']}\n\n"
            f"Imports réels à utiliser :\n{imports_hint}\n\n"
            f"Classe(s) disponible(s) ({len(matched_classes)}) :\n{classes_desc}\n\n"
            f"{field_allowlist_block}\n\n"
            f"{values_block}\n\n"
            f"Rappel : réponds UNIQUEMENT avec un bloc ```python contenant le "
            f"script complet, sans aucun texte avant/après, sans commentaire, "
            f"en commençant par `import sys`."
        )
    if feedback:
        human += f"\n\nFEEDBACK D'UNE EXÉCUTION PRÉCÉDENTE (corrige le script généré) :\n{feedback}"
    return human


def _build_field_allowlist_reminder(matched_classes: list[ClassInfo], class_lookup: dict[str, ClassInfo]) -> str:
    """[FIX-B] Version compacte du bloc de contrainte, pour les messages de
    retry (répéter la contrainte à chaque tentative)."""
    parts: list[str] = []
    for ci in matched_classes:
        all_fields = resolve_all_fields(ci, class_lookup)
        legal = ", ".join(f.name for f in all_fields) if all_fields else "(aucun)"
        parts.append(f"{ci.name}: [{legal}]")
    return "RAPPEL CHAMPS LÉGAUX (uniquement ces noms) : " + " | ".join(parts)


def generate_llm_script(
    scenario: dict,
    matched_classes: list[ClassInfo],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
    llm,
    flync_src_root: Path,
    feedback: Optional[str] = None,
    max_retries: int = 2,
    resolved_via_rag: Optional[list[str]] = None,
    known_modules: Optional[set[str]] = None,
    timeout_seconds: int = DEFAULT_EXECUTION_TIMEOUT_SECONDS,   # [REVUE-2]
) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    human_prompt = _construire_prompt_humain_mono(
        scenario, matched_classes, validators_by_class, class_lookup,
        feedback, resolved_via_rag,
    )
    messages = [SystemMessage(content=_SYSTEM_PROMPT_LLM_MONO), HumanMessage(content=human_prompt)]
    allowed_names = classes_potentiellement_necessaires(matched_classes, class_lookup)

    field_allowlist_reminder = _build_field_allowlist_reminder(matched_classes, class_lookup)

    scenario_values = extract_scenario_values(scenario)
    known_field_names: set[str] = set()
    for ci in matched_classes:
        known_field_names |= {f.name for f in resolve_all_fields(ci, class_lookup)}

    attempt_errors: list[tuple[int, str, str]] = []
    for attempt in range(1, max_retries + 2):
        response = llm.invoke(messages)
        code = extraire_code_python(response.content)

        error = valider_syntaxe(code)
        error_kind = "syntaxe"
        if error is None:
            error = valider_classes_autorisees(code, allowed_names)
            error_kind = "classes hors périmètre / shadowing"
        if error is None:
            error = valider_imports_flync(code, known_modules, class_lookup)
            error_kind = "import de module/symbole FLYNC halluciné"
        if error is None and scenario.get("type") == "Negative":
            error = valider_contrat_negative(code)
            error_kind = "contrat exit-code Negative violé"
        if error is None:
            exec_result = execute_generated_script(code, flync_src_root, timeout_seconds=timeout_seconds)
            if not exec_result.success:
                error = format_execution_error(exec_result)
                error_kind = "exécution réelle"
        if error is None:
            error = valider_fidelite_valeurs(code, scenario_values, known_field_names)
            error_kind = "valeurs du scénario non respectées"
        if error is None:
            return code

        attempt_errors.append((attempt, error_kind, error))
        print(f"[{AGENT_LABEL}] {scenario['id']}: {error_kind} invalide (tentative {attempt}) -> {error}")


        messages.append(response)
        messages.append(HumanMessage(content=(
            f"Le code précédent est rejeté ({error_kind}) : {error}\n\n"
            f"{field_allowlist_reminder}\n\n"
            f"Renvoie UNIQUEMENT le code Python corrigé, sous forme d'un unique "
            f"bloc ```python, en commençant par `import sys`, sans aucun texte "
            f"hors du code, sans commentaire."
        )))

    kinds_seen = [k for _, k, _ in attempt_errors]
    repeated = len(set(kinds_seen)) == 1 and len(kinds_seen) > 1
    history = "\n".join(f"  tentative {a}: [{k}] {m}" for a, k, m in attempt_errors)
    suffix = " (même type d'erreur à chaque tentative -- hallucination probablement stable)" if repeated else ""
    raise LLMGenerationError(
        f"{scenario['id']}: échec de génération LLM après {max_retries + 1} tentative(s){suffix}.\n{history}"
    )



@dataclass
class MonoScenarioPlan:
    scenario: dict
    verdict: ScenarioVerdict
    category: str  # "mono_module" | "requires_sdk" | "unresolved"


def classify_mono_scenario(
    scenario: dict,
    kb_index,
    class_lookup: dict[str, ClassInfo],
    relation_graph,
    retriever,
) -> MonoScenarioPlan:
    verdict = verify_scenario(scenario, kb_index, class_lookup, relation_graph, retriever)

    if len(verdict.submodels_declared) >= 2:
        print(
            f"[{AGENT_LABEL}] INCOHÉRENCE: {scenario['id']} vient du fichier "
            f"mono-module mais submodel='{scenario['submodel']}' déclare "
            f"{len(verdict.submodels_declared)} sous-modèles "
            f"({', '.join(verdict.submodels_declared)}). Traité quand même "
            f"comme mono -- à corriger côté fichier KPIT source."
        )

    category = (
        "requires_sdk" if verdict.classification == "REQUIRES_SDK" else
        "unresolved" if verdict.classification == "UNRESOLVED" else
        "mono_module"
    )
    return MonoScenarioPlan(scenario=scenario, verdict=verdict, category=category)


def _has_any_real_validator(validators_by_class: dict[str, list[str]]) -> bool:
    """Retourne True si au moins une classe du verdict possède un validator
    Pydantic réel (i.e. pas la sentinelle '(aucun validator)')."""
    return any(
        v for validators in validators_by_class.values()
        for v in validators if v != "(aucun validator)"
    )


_CONSTRAINT_MARKERS = ("gt=", "ge=", "lt=", "le=", "pattern=", "regex=", "min_length=", "max_length=")


def _scenario_value_likely_violates_constraint(
    scenario_values: dict[str, object],
    matched_classes: list[ClassInfo],
    class_lookup: dict[str, ClassInfo],
) -> bool:
    """[FIX-12] Heuristique : au moins une valeur extraite du scénario
    correspond à un champ réel ET ce champ porte une contrainte Pydantic
    explicite dans son Field(...). Ne PROUVE pas que la valeur viole la
    contrainte (on ne parse pas les bornes numériques/regex), mais filtre le
    cas majoritaire observé en production (SC-TSN-005-NEG) : un champ SANS
    aucune contrainte ne peut de toute façon jamais lever de ValidationError
    sur sa valeur, quel que soit le placeholder choisi par le gabarit."""
    if not scenario_values:
        return False
    all_fields: dict[str, FieldInfo] = {}
    for ci in matched_classes:
        for f in resolve_all_fields(ci, class_lookup):
            all_fields[f.name] = f
    for key in scenario_values:
        f = all_fields.get(key)
        if f is not None and f.default_str and any(m in f.default_str for m in _CONSTRAINT_MARKERS):
            return True
    return False


def decide_mode(
    scenario: dict,
    verdict: ScenarioVerdict,
    cli_mode: str,
    matched_classes: Optional[list[ClassInfo]] = None,
    class_lookup: Optional[dict[str, ClassInfo]] = None,
) -> str:
    if verdict.classification != "MODEL_ONLY":
        return cli_mode
    if cli_mode != "template":
        return cli_mode
    if scenario.get("type") != "Negative":
        return "template"

    if not _has_any_real_validator(verdict.validators_on_matched_classes):
        print(
            f"[{AGENT_LABEL}] {scenario['id']}: Negative sans validator local "
            f"connu sur les classes résolues -- bascule vers LLM."
        )
        return "llm"

    if matched_classes is not None and class_lookup is not None:
        scenario_values = extract_scenario_values(scenario)
        if not _scenario_value_likely_violates_constraint(scenario_values, matched_classes, class_lookup):
            print(
                f"[{AGENT_LABEL}] {scenario['id']}: Negative avec validator mais "
                f"aucune valeur du scénario ne correspond à un champ contraint "
                f"(gt/lt/pattern/...) -- le gabarit ne peut pas garantir de "
                f"déclencher la faute, bascule vers LLM."
            )
            return "llm"

    return "template"


def _print_classification_report(plans: list[MonoScenarioPlan]) -> None:
    counts: dict[str, int] = {}
    for p in plans:
        counts[p.category] = counts.get(p.category, 0) + 1
    print(f"\n[{AGENT_LABEL}] ===== Rapport de classification (0 appel LLM) =====")
    for category in ("mono_module", "requires_sdk", "unresolved"):
        print(f"[{AGENT_LABEL}]   {category:14s} : {counts.get(category, 0)}")
    print(f"[{AGENT_LABEL}] " + "=" * 58 + "\n")



def _make_out_of_scope_script(scenario: dict) -> str:
    sid = scenario["id"]
    fault = scenario.get("injected_fault", "unknown fault")
    title = scenario.get("title", "")
    return (
        "import sys\n\n"
        f"# OUT_OF_SCOPE: {sid}\n"
        f"# title: {title}\n"
        f"# injected_fault: {fault}\n"
        f"# Aucun validator Pydantic réel sur les classes résolues ne peut\n"
        f"# reproduire cette faute en isolation. Un test d'intégration\n"
        f"# au niveau FLYNCModel complet est requis.\n"
        'print("OUT_OF_SCOPE: no validator can reproduce this fault in isolation")\n'
        "sys.exit(1)\n"
    )


def process_one_mono_scenario(
    plan: MonoScenarioPlan,
    class_lookup: dict[str, ClassInfo],
    cli_mode: str,
    llm,
    flync_src_root: Path,
    output_dir: Path,
    llm_max_retries: int,
    known_modules: Optional[set[str]] = None,
    timeout_seconds: int = DEFAULT_EXECUTION_TIMEOUT_SECONDS,   # [REVUE-2]
) -> ScenarioProcessingResult:
    scenario = plan.scenario
    verdict = plan.verdict
    matched_classes = resolve_matched_classes(
        verdict.entities_found_in_model, class_lookup, scenario["id"], AGENT_LABEL
    )
    validators_by_class = verdict.validators_on_matched_classes
    exec_success: Optional[bool]

    if plan.category == "requires_sdk":
        content = (
            "import sys\n\n"
            'print("ERROR: scenario requires SDK, out of current KB scope")\n'
            "sys.exit(1)\n"
        )
        exec_success = None

    elif plan.category == "unresolved":
        content = (
            "import sys\n\n"
            'print("ERROR: no matching FLYNC class resolved for this scenario")\n'
            "sys.exit(1)\n"
        )
        exec_success = None

    else:
        impossible, reason = is_scenario_isolation_impossible(scenario)
        if impossible:
            print(
                f"[{AGENT_LABEL}] {scenario['id']}: OUT_OF_SCOPE ({reason}) -- "
                f"ce scénario décrit une contrainte globale/cross-instance "
                f"impossible à reproduire en test unitaire isolé."
            )
            content = _make_out_of_scope_script(scenario)
            exec_success = None
            plan = MonoScenarioPlan(
                scenario=plan.scenario,
                verdict=plan.verdict,
                category="out_of_scope",
            )
            out_path = output_path_for(
                plan.category, scenario["id"], scenario.get("type", "unknown"), output_dir
            )
            out_path.write_text(content, encoding="utf-8")
            return ScenarioProcessingResult(
                scenario_id=scenario["id"],
                agent="mono",
                category="out_of_scope",
                n_matched_classes=len(matched_classes),
                out_path=out_path,
                execution_success=None,
                error=f"OUT_OF_SCOPE: {reason}",
            )

        effective_mode = decide_mode(scenario, verdict, cli_mode, matched_classes, class_lookup)
        if effective_mode == "template":
            content, warnings = generate_construction_script(
                scenario, matched_classes, validators_by_class, class_lookup
            )
            for w in warnings:
                print(f"[{AGENT_LABEL}] AVERTISSEMENT: {w}")
            # [REVUE-2] timeout_seconds propagé.
            exec_result = execute_generated_script(content, flync_src_root, timeout_seconds=timeout_seconds)
            exec_success = exec_result.success
            if not exec_result.success:
                print(
                    f"[{AGENT_LABEL}] {scenario['id']}: ÉCHEC D'EXÉCUTION "
                    f"(template, pas de retry) -> "
                    f"{format_execution_error(exec_result)}"
                )

        else:  
            try:
                content = generate_llm_script(
                    scenario, matched_classes, validators_by_class, class_lookup,
                    llm, flync_src_root,
                    max_retries=llm_max_retries,
                    resolved_via_rag=verdict.resolved_via_rag,
                    known_modules=known_modules,
                    timeout_seconds=timeout_seconds,   # [REVUE-2]
                )
                exec_success = True

            except LLMGenerationError as exc:
                print(f"[{AGENT_LABEL}] {exc}")

                is_negative = scenario.get("type") == "Negative"
                if is_negative and not _has_any_real_validator(validators_by_class):
                    print(
                        f"[{AGENT_LABEL}] {scenario['id']}: OUT_OF_SCOPE -- "
                        f"aucun validator ne peut reproduire la faute en isolation. "
                        f"Script stub N/A généré (pas de repli gabarit voué à l'échec)."
                    )
                    content = _make_out_of_scope_script(scenario)
                    exec_success = None
                    plan = MonoScenarioPlan(
                        scenario=plan.scenario,
                        verdict=plan.verdict,
                        category="out_of_scope",
                    )

                else:
                    print(f"[{AGENT_LABEL}] -> repli sur le gabarit pour ce scénario.")
                    content, warnings = generate_construction_script(
                        scenario, matched_classes, validators_by_class, class_lookup
                    )
                    for w in warnings:
                        print(f"[{AGENT_LABEL}] AVERTISSEMENT: {w}")
                    # [REVUE-2] timeout_seconds propagé également sur ce repli.
                    exec_result = execute_generated_script(content, flync_src_root, timeout_seconds=timeout_seconds)
                    exec_success = exec_result.success

    out_path = output_path_for(
        plan.category, scenario["id"], scenario.get("type", "unknown"), output_dir
    )
    out_path.write_text(content, encoding="utf-8")

    return ScenarioProcessingResult(
        scenario_id=scenario["id"],
        agent="mono",
        category=plan.category,
        n_matched_classes=len(matched_classes),
        out_path=out_path,
        execution_success=exec_success,
    )



def run_mono_agent(
    scenarios: list[dict],
    ctx: SharedContext,
    cli_mode: str,
    llm,
    output_dir: Path,
    llm_max_retries: int,
    max_workers: int,
    timeout_seconds: int = DEFAULT_EXECUTION_TIMEOUT_SECONDS,   # [REVUE-2]
) -> list[ScenarioProcessingResult]:
    print(
        f"[{AGENT_LABEL}] Classification de {len(scenarios)} scénario(s) "
        f"mono-module (0 appel LLM)..."
    )
    plans = [
        classify_mono_scenario(
            s, ctx.kb_index, ctx.class_lookup, ctx.relation_graph, ctx.retriever
        )
        for s in scenarios
    ]
    _print_classification_report(plans)

    results: list[ScenarioProcessingResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_plan = {
            executor.submit(
                process_one_mono_scenario, plan, ctx.class_lookup, cli_mode,
                llm, ctx.flync_src_root, output_dir, llm_max_retries,
                known_modules=ctx.known_modules,
                timeout_seconds=timeout_seconds,   # [REVUE-2]
            ): plan
            for plan in plans
        }
        for future in concurrent.futures.as_completed(future_to_plan):
            plan = future_to_plan[future]
            try:
                result = future.result()
                results.append(result)
                if result.execution_success is None:
                    status = "N/A"
                elif result.execution_success:
                    status = "OK"
                else:
                    status = "ÉCHEC EXÉCUTION"
                print(
                    f"[{AGENT_LABEL}] {result.scenario_id} "
                    f"({plan.category}, {result.n_matched_classes} classe(s), "
                    f"exécution={status}) -> {result.out_path}"
                )
            except Exception as exc:
                sid = plan.scenario["id"]
                print(f"[{AGENT_LABEL}] ERREUR CRITIQUE sur {sid}: {exc}")
                results.append(ScenarioProcessingResult(
                    scenario_id=sid,
                    agent="mono",
                    category="error",
                    n_matched_classes=0,
                    out_path=None,
                    execution_success=False,
                    error=str(exc),
                ))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Développeur Mono-Module.")
    parser.add_argument(
        "--scenarios", required=True,
        help="Fichier JSON des scénarios mono-module UNIQUEMENT.",
    )
    parser.add_argument("--mode", choices=["template", "llm"], default="template")
    parser.add_argument(
        "--llm-backend", choices=["ollama", "anthropic", "gemini", "groq"], default=None
    )
    parser.add_argument("--llm-max-retries", type=int, default=2)
    parser.add_argument("--output-dir", default="./generated_scripts")
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_EXECUTION_TIMEOUT_SECONDS)
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenarios)
    ctx = build_shared_context()
    llm = get_llm(args.llm_backend, category="MONO_MODULE") if args.mode == "llm" else None

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    results = run_mono_agent(
        scenarios, ctx, args.mode, llm, output_dir,
        args.llm_max_retries, args.max_workers,
        timeout_seconds=args.timeout_seconds,   # [REVUE-2]
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
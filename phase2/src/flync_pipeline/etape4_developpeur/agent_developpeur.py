
from __future__ import annotations

import argparse
import ast
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from phase2.src.flync_pipeline.etape2_lecteur.agent_lecteur_analyste import AgentLecteurAnalyste, ClassInfo, FieldInfo
from phase2.src.flync_pipeline.etape1_discovery.kb_pointers import FLYNC_KB
from phase2.src.flync_pipeline.etape2_lecteur.module_relations import build_module_relation_graph
from phase2.src.flync_pipeline.etape3_verificateur.scenario_verifier import KBIndex, resolve_submodel_field, verify_scenario
from phase2.src.flync_pipeline.etape4_developpeur.commun import get_llm


class LLMGenerationError(RuntimeError):
    """Levée quand le LLM n'a pas réussi à produire un script Python
    syntaxiquement valide, autorisé, ET exécutable avec succès, après
    --llm-max-retries tentatives."""



DEFAULT_EXECUTION_TIMEOUT_SECONDS = 30


@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    returncode: Optional[int]
    timed_out: bool


def execute_generated_script(
    code: str,
    flync_src_root: Path,
    timeout_seconds: int = DEFAULT_EXECUTION_TIMEOUT_SECONDS,
) -> ExecutionResult:
  
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp_file:
        tmp_file.write(code)
        tmp_path = tmp_file.name

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(flync_src_root) + (
        os.pathsep + existing_pythonpath if existing_pythonpath else ""
    )

    try:
        completed = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
        )
        return ExecutionResult(
            success=completed.returncode == 0,
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        return ExecutionResult(
            success=False,
            stdout=exc.stdout or "",
            stderr=f"Timeout d'exécution dépassé ({timeout_seconds}s).",
            returncode=None,
            timed_out=True,
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _format_execution_error(exec_result: ExecutionResult) -> str:
    """Message d'erreur exploitable en feedback LLM à partir d'un échec
    d'exécution réel (returncode != 0)."""
    if exec_result.timed_out:
        return exec_result.stderr
    return (
        f"Le script s'est exécuté avec le code de sortie {exec_result.returncode} "
        f"(attendu: 0). stderr réel :\n{exec_result.stderr.strip()}\n"
        f"stdout réel :\n{exec_result.stdout.strip()}"
    )



_ANNOTATED_RE = re.compile(r"^Annotated\[\s*([^,]+?)\s*,")
_MAX_NESTED_DEPTH = 3


def infer_placeholder(
    field_info: FieldInfo,
    class_lookup: dict[str, ClassInfo],
    _depth: int = 0,
    _visited: Optional[frozenset[str]] = None,
    _referenced_classes: Optional[set[str]] = None,
) -> tuple[str, bool]:
    if _visited is None:
        _visited = frozenset()
    t = field_info.type_str.strip()

    m = _ANNOTATED_RE.match(t)
    if m:
        inner_type = m.group(1).strip()
        inner_field = FieldInfo(field_info.name, inner_type, field_info.required, field_info.default_str)
        return infer_placeholder(inner_field, class_lookup, _depth, _visited, _referenced_classes)

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
            if not nf.required:
                continue
            nv, n_resolved = infer_placeholder(nf, class_lookup, _depth + 1, nested_visited, _referenced_classes)
            all_nested_resolved = all_nested_resolved and n_resolved
            nested_parts.append(f"{nf.name}={nv}")
        return f"{referenced.name}({', '.join(nested_parts)})", all_nested_resolved

    return "None", False


def resolve_all_fields(class_info: ClassInfo, class_lookup: dict[str, ClassInfo]) -> list[FieldInfo]:
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
) -> tuple[list[str], list[str]]:
    var_name = _var_name_for(class_info)
    lines = [f"{indent}{var_name} = {class_info.name}("]
    warnings: list[str] = []
    for f in resolve_all_fields(class_info, class_lookup):
        if not f.required:
            continue
        value, resolved = infer_placeholder(f, class_lookup, _referenced_classes=referenced_classes)
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
    submodels_actually_linked: Optional[bool] = None,
) -> tuple[str, list[str]]:
    scenario_id = scenario["id"]
    scenario_type = scenario["type"]
    warnings: list[str] = []

    if not matched_classes:
        content = (
            "import sys\n\n"
            'print("ERROR: no matching FLYNC class resolved for this scenario")\n'
            "sys.exit(1)\n"
        )
        return content, [f"{scenario_id}: aucune classe résolue -- script de repli (exit=1) généré"]

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
                f"{scenario_id}: GAP -- {ci.name} n'a aucun validator connu ; en attendant "
                f"clarification KPIT, la branche ValidationError ne sera probablement pas "
                f"atteinte via cette classe."
            )

    if len(matched_classes) > 1:
        warnings.append(
            f"{scenario_id}: scénario cross-module -- {len(matched_classes)} classes "
            f"construites dans le même script : {', '.join(ci.name for ci in matched_classes)}"
        )
        if submodels_actually_linked is False:
            warnings.append(
                f"{scenario_id}: ⚠️ SCÉNARIO SUSPECT -- déclaré cross_module mais AUCUN couplage "
                f"réel (import croisé AST) trouvé entre les modules déclarés."
            )
        elif submodels_actually_linked is True:
            warnings.append(
                f"{scenario_id}: couplage réel confirmé entre les modules déclarés "
                f"(import croisé AST trouvé)."
            )

    indent = "    " if scenario_type == "Negative" else ""
    all_construction_lines: list[str] = []
    referenced_classes: set[str] = set()
    for ci in matched_classes:
        lines, field_warnings = build_construction_snippet(
            ci, class_lookup, indent=indent, referenced_classes=referenced_classes
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



_CODE_FENCE_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extraire_code_python(text: str) -> str:
    blocks = _CODE_FENCE_RE.findall(text)
    if blocks:
        return max(blocks, key=len).strip()
    return text.strip()


def valider_syntaxe(code: str) -> Optional[str]:
    try:
        compile(code, "<generated>", "exec")
        return None
    except SyntaxError as exc:
        return f"{type(exc).__name__}: {exc}"


def _classes_potentiellement_necessaires(
    matched_classes: list[ClassInfo],
    class_lookup: dict[str, ClassInfo],
) -> set[str]:
    allowed: set[str] = set()
    seen_class_names: set[str] = set()

    _TYPE_NAME_RE = re.compile(r"[A-Z][A-Za-z0-9_]*")

    def _walk(ci: ClassInfo) -> None:
        if ci.name in seen_class_names:
            return
        seen_class_names.add(ci.name)
        allowed.add(ci.name)

        for base_name in ci.bases:
            allowed.add(base_name)
            base_info = class_lookup.get(base_name)
            if base_info is not None:
                _walk(base_info)

        for f in ci.fields:
            for candidate in _TYPE_NAME_RE.findall(f.type_str):
                if candidate in class_lookup:
                    allowed.add(candidate)
                    _walk(class_lookup[candidate])

    for ci in matched_classes:
        _walk(ci)

    return allowed


_BUILTIN_ALLOWED_CALLS = {
    "str", "int", "float", "bool", "list", "dict", "set", "tuple", "bytes",
    "print", "sys", "Path", "ValidationError", "Field", "BaseModel",
    "IPvAnyAddress", "IPv4Address", "IPv6Address", "IPv4Network", "IPv6Network",
    "UUID", "Decimal", "Enum",
}


def valider_classes_autorisees(code: str, allowed_names: set[str]) -> Optional[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"{type(exc).__name__}: {exc}"

    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add((alias.asname or alias.name).split(".")[0])

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in imported_names:
            return (
                f"Le code redéfinit localement la classe '{node.name}' qui a été importée "
                f"depuis le vrai module FLYNC -- interdit, cela masquerait le modèle réel."
            )

    allowed = allowed_names | _BUILTIN_ALLOWED_CALLS | imported_names
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            call_name = node.func.id
            if call_name[0:1].isupper() and call_name not in allowed:
                return (
                    f"Le code instancie '{call_name}(...)', qui n'appartient ni aux classes "
                    f"fournies par le Vérificateur, ni à leurs types de champs imbriqués. "
                    f"Classes autorisées : {', '.join(sorted(allowed_names)) or '(aucune)'}."
                )

    return None



_SYSTEM_PROMPT_LLM = (
    "Tu es un générateur de code Python pour le framework FLYNC (modèles "
    "Pydantic v2 réels, pas une simulation).\n\n"
    "FORMAT DE RÉPONSE, ABSOLU ET NON NÉGOCIABLE :\n"
    "- Ta réponse ENTIÈRE doit être un unique bloc ```python ... ``` et rien "
    "d'autre. Aucune phrase avant, aucune phrase après, aucune explication.\n"
    "- Le code ne doit contenir NI commentaire (#), NI docstring, NI texte "
    "quelconque : uniquement des instructions Python exécutables.\n"
    "- N'écris jamais 'Voici', 'Ce code', 'Notez que' ou toute autre phrase "
    "en langage naturel, même en dehors du bloc de code.\n\n"
    "RÈGLES DE CONTENU :\n"
    "1. CE N'EST PAS UN TEST : n'importe jamais pytest, n'écris jamais assert, "
    "jamais pytest.raises, jamais de fonction test_*().\n"
    "2. Si PLUSIEURS classes sont listées ci-dessous (scénario cross-module), "
    "instancie-les TOUTES dans le même script, avec un import par classe.\n"
    "3. Chaque valeur de champ doit être concrète et plausible, jamais un "
    "placeholder générique. Utilise la valeur EXACTE du scénario quand elle "
    "est donnée. Pour Positive, respecte les contraintes réelles. Pour "
    "Negative, utilise la valeur fautive exacte lorsqu'elle est fournie ou "
    "construis une valeur qui viole réellement la contrainte identifiée par "
    "le Vérificateur. Ne transforme jamais une faute métier en simple valeur "
    "arbitraire sans vérifier le mécanisme réel qui doit la détecter.\n"
    "4. N'invente JAMAIS un champ, une classe ou un validator non listés. Utilise UNIQUEMENT les "
    "classes explicitement listées ci-dessous (ou leurs types de champs imbriqués également listés) -- "
    "jamais une classe qui te semble plausible pour le domaine (ex: ne pas inventer "
    "ServiceConsumerReference si seule AppBindings est fournie).\n"
    "4ter. N'IMPORTE PAS puis REDÉFINIS une classe FLYNC : si tu écris "
    "`from flync.model... import AppBindings`, n'écris JAMAIS ensuite `class AppBindings(...):`. "
    "Cela masquerait l'import réel et ferait tester un faux modèle bidon au lieu du vrai.\n"
    "4bis. Si une classe listée est marquée [ENUM], ne l'instancie JAMAIS avec "
    "des parenthèses (ex: SignalDataType(...) est INTERDIT) : référence un de "
    "ses membres listés (ex: SignalDataType.UINT16).\n"
    "5. Utilise les imports réels donnés, jamais un chemin deviné.\n\n"
    "CONTRAT D'EXIT CODE, STRICT ET SANS EXCEPTION :\n"
    "- `import sys` est TOUJOURS la toute première ligne du script, avant "
    "tout autre import, dans TOUS les cas -- ce script sera réellement "
    "exécuté (pas seulement relu), un `import sys` manquant provoque un "
    "NameError immédiat sur `sys.exit(...)` et fait échouer le script.\n"
    "- Si scenario['type'] == 'Positive' : instanciation réelle de TOUS les "
    "objets, SANS try/except, puis print(\"SUCCESS\") puis sys.exit(0). Ne "
    "jamais intercepter une exception imprévue.\n"
    "- Si scenario['type'] == 'Negative' : `from pydantic import "
    "ValidationError`, puis TOUTE la construction (un ou plusieurs objets) "
    "dans un seul bloc :\n"
    "    try:\n"
    "        obj = RealFlyncClass(..., faulty_value=...)\n"
    "    except ValidationError as exc:\n"
    "        print(f\"EXPECTED ERROR: {exc}\")\n"
    "        sys.exit(0)\n"
    "    except Exception as exc:\n"
    "        print(f\"UNEXPECTED ERROR: {type(exc).__name__}: {exc}\")\n"
    "        sys.exit(1)\n"
    "    else:\n"
    "        print(\"ERROR: expected ValidationError but no error was raised\")\n"
    "        sys.exit(1)\n\n"
    "ANALYSE ET EXÉCUTION DU PLAN :\n"
    "6. ANALYSE DE LA SÉMANTIQUE DU SCÉNARIO : la description, le résultat "
    "attendu et la faute injectée décrivent le comportement métier que le script doit "
    "reproduire. Toute relation ou contrainte explicitement demandée doit "
    "être matérialisée dans le script SI une classe, un champ, un validator "
    "ou un mécanisme réel fourni ci-dessous permet de la représenter.\n"
    "7bis. REPRODUCTION DES RELATIONS MÉTIER : si la description du scénario "
    "mentionne explicitement une relation entre plusieurs entités (par exemple "
    "'NavigationApp' liée à 'hpc_controller1', ou un contrôleur ECU déclaré "
    "comme participating node d'un bus), le script doit reproduire cette "
    "relation RÉELLE si elle est représentable par les classes, champs, modèles "
    "imbriqués ou mécanismes de validation fournis ci-dessous. "
    "Ne construis pas des objets indépendants qui ignorent la relation décrite.\n"
    "    - Identifie toutes les entités explicitement citées dans le scénario.\n"
    "    - Cherche dans les champs et types réels fournis comment ces entités "
    "    sont reliées (un champ de l'une référence probablement un identifiant "
    "    ou un nom de l'autre).\n"
    "    - Si une classe disponible représente l'autre extrémité de la relation, "
    "    construis également cette classe dans le même script, avec des "
    "    identifiants/noms COHÉRENTS entre les objets liés (même valeur de "
    "    référence des deux côtés).\n"
    "    - Si la relation est portée par un champ de l'objet principal, renseigne "
    "    ce champ avec la valeur exacte donnée dans le scénario.\n"
    "    - Si plusieurs objets doivent être construits pour représenter la "
    "    relation, construis-les tous, avec les valeurs de liaison cohérentes.\n"
    "    - N'invente JAMAIS un champ ou une relation simplement parce que le "
    "    scénario la décrit : la relation doit être confirmée par les classes, "
    "    champs, validators ou mécanismes réels fournis.\n"
    "    - Si la relation décrite par le scénario n'est pas représentable avec "
    "    les éléments disponibles, ne fabrique pas de liaison artificielle : "
    "    construis uniquement ce qui est réellement représentable, et laisse "
    "    les objets non liés si aucun champ ne permet de les relier.\n"
    "8. REPRODUCTION EXACTE DE LA FAUTE : pour un scénario Negative, la "
    "construction doit provoquer réellement la faute décrite selon le mécanisme Pydantic sous-jacent.\n"
    "9. VALIDATION DISPONIBLE UNIQUEMENT : ne suppose pas qu'une ValidationError sera "
    "levée si le mécanisme réel est absent des modèles fournis. Si la validation n'existe pas "
    "dans le code réel, n'invente rien et ne simule pas l'erreur.\n"
    "10. LE PLAN DE CONSTRUCTION FOURNI EST LA SOURCE DE VÉRITÉ ABSOLUE. "
    "N'invente aucun mécanisme de substitution si les classes fournies ne "
    "permettent pas de représenter un aspect du scénario.\n"
    "11. INTERDICTION DE MOCKING OU STRUCT LOCALES : il est strictement interdit "
    "de créer des classes locales, classes Meta, validators custom locaux ou stubs. "
    "Le script doit utiliser exclusivement les modèles importés du package FLYNC.\n"
    "12. REPRODUCTION GENERIQUE DES FAUTES NEGATIVE : pour TOUT scénario "
    "Negative, reproduis la faute décrite en utilisant UNIQUEMENT les "
    "mécanismes réels identifiés (contrainte Pydantic locale, validator, "
    "relation entre plusieurs objets, contrainte d'unicité, référence, "
    "contrainte inter-module, ou tout autre mécanisme réel explicitement "
    "visible dans les classes fournies).\n"
    "13. SOURCE DE VERITE POUR LA FAUTE : ne déduis, n'invente et ne remplace "
    "JAMAIS le mécanisme de validation décrit par le scénario.\n"
    "14. FAUTES LOCALES ET GLOBALES : si une faute nécessite plusieurs objets "
    "ou plusieurs composants, construis TOUS les objets requis. Ne suppose "
    "jamais qu'une simple instanciation suffit pour une contrainte globale.\n"
    "15. AUCUNE VALIDATION IMAGINAIRE : deux objets identiques, deux valeurs "
    "identiques ou une relation décrite dans le texte ne provoquent pas "
    "automatiquement une ValidationError. Une erreur ne doit être attendue "
    "que si les modèles/validators réels fournis contiennent un mécanisme "
    "capable de la déclencher.\n"
    "16. INTERDICTION DE SIMULATION : si le mécanisme réel n'existe pas dans "
    "les modèles, validators ou mécanismes explicitement fournis, ne crée "
    "aucune classe, Meta, validator, registre, dictionnaire, fonction ou autre "
    "logique locale pour simuler la faute. Utilise uniquement les éléments "
    "réels disponibles ci-dessous.\n"
    "17. SCÉNARIOS CROSS-MODULE : lorsqu'un scénario concerne plusieurs "
    "sous-modèles FLYNC, traite-les comme un scénario unique et utilise "
    "TOUTES les classes explicitement fournies pour les modules concernés. "
    "Le script doit contenir les imports réels et les instanciations "
    "nécessaires pour chaque classe requise.\n"
    "18. RELATION CROSS-MODULE RÉELLE : pour un scénario cross-module, ne "
    "suppose jamais que la présence de deux classes dans deux sous-modèles "
    "implique automatiquement une relation entre elles. Une relation entre "
    "modules ne peut être utilisée que si elle est explicitement identifiée "
    "dans les informations réelles fournies (champ de l'une référençant "
    "l'autre, identifiant partagé, etc.).\n"
    "19. CONSTRUCTION DE LA RELATION : si une relation réelle entre les "
    "modules est identifiable, construis les objets dans le script en "
    "respectant exactement cette relation, avec les champs, références, "
    "types et valeurs réellement disponibles. N'invente aucun champ ou "
    "mécanisme de liaison.\n"
    "20. CROSS-MODULE SANS COUPLAGE RÉEL : si aucun couplage réel n'existe "
    "entre les modules concernés (voir note ci-dessous si présente), "
    "construis uniquement les objets réels nécessaires de chaque module, "
    "indépendamment les uns des autres. N'ajoute aucune référence "
    "artificielle, aucun champ de liaison, aucun wrapper, aucune classe "
    "intermédiaire et aucune logique locale pour simuler une interaction.\n"
    "21. CROSS-MODULE NEGATIVE : si un scénario cross-module est Negative, "
    "détermine si la faute concerne un seul objet, plusieurs objets ou la "
    "relation entre les modules, et construis exactement ce que ça implique.\n"
    "22. NOMBRE DE CLASSES : construis toutes les classes explicitement "
    "requises par les informations fournies, et aucune classe supplémentaire.\n\n"
    "VALIDATION RÉELLE (nouveau) :\n"
    "23. Ce script est ENSUITE RÉELLEMENT EXÉCUTÉ (subprocess Python "
    "isolé) avant d'être accepté -- pas seulement vérifié syntaxiquement. "
    "S'il échoue à l'exécution (NameError, ImportError, AttributeError, "
    "TypeError, ValidationError inattendue...), tu recevras le vrai "
    "traceback réel et devras corriger en conséquence.\n"
)


def _construire_prompt_humain(
    scenario: dict,
    matched_classes: list[ClassInfo],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
    feedback: Optional[str],
    submodels_actually_linked: Optional[bool] = None,
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
                constraint = f" | contrainte réelle: {f.default_str}" if f.default_str and "Field(" in (f.default_str or "") else ""
                inner_type = _ANNOTATED_RE.match(f.type_str.strip())
                inner_type = inner_type.group(1).strip() if inner_type else f.type_str.strip()
                referenced = class_lookup.get(inner_type)
                type_note = ""
                if referenced is not None and referenced.is_enum:
                    type_note = f" | [ENUM, membres: {', '.join(referenced.enum_members) or 'aucun détecté'}]"
                field_lines.append(f"  - {f.name}: {f.type_str} | obligatoire={f.required}{constraint}{type_note}")
            class_validators = [v for v in validators_by_class.get(ci.name, []) if v != "(aucun validator)"]
            rag_note = (
                "\n[NOTE: cette classe a été résolue par similarité sémantique (RAG), "
                "pas par mention exacte de son nom dans le scénario -- confiance modérée, "
                "vérifie sa pertinence avant de l'utiliser telle quelle]"
                if ci.name in resolved_via_rag else ""
            )
            blocks.append(
                f"{ci.name} (module réel: {ci.module}, fichier: {ci.file}){rag_note}\n"
                f"Champs (avec héritage résolu) :\n" + "\n".join(field_lines) + "\n"
                f"Validators réels sur cette classe : {class_validators or '(aucun)'}"
            )
            module_file_stem = ci.file.removesuffix(".py")
            import_lines.append(f"from flync.model.{ci.module}.{module_file_stem} import {ci.name}")
        classes_desc = "\n\n".join(blocks)
        imports_hint = "\n".join(import_lines)

    human = (
        f"Scénario : {scenario['id']} ({scenario['type']})\n"
        f"Titre : {scenario['title']}\n"
        f"Description : {scenario['description']}\n"
        f"Fault injecté : {scenario.get('injected_fault')}\n"
        f"Résultat attendu : {scenario['expected_result']}\n\n"
        f"Imports réels à utiliser :\n{imports_hint}\n\n"
        f"Classe(s) disponible(s) ({len(matched_classes)}) :\n{classes_desc}\n\n"
        f"Rappel : réponds UNIQUEMENT avec un bloc ```python contenant le "
        f"script complet, sans aucun texte avant/après, sans commentaire, "
        f"en commençant par `import sys`."
    )
    if len(matched_classes) > 1 and submodels_actually_linked is False:
        human += (
            "\n\nATTENTION : ce scénario est déclaré cross-module, mais aucun couplage réel "
            "n'a été trouvé entre les modules concernés. N'invente donc AUCUNE relation "
            "artificielle entre ces objets."
        )
    if feedback:
        human += (
            "\n\nFEEDBACK D'UNE EXÉCUTION PRÉCÉDENTE (corrige le script généré) :\n"
            f"{feedback}"
        )
    return human


def generate_llm_script(
    scenario: dict,
    matched_classes: list[ClassInfo],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
    llm,
    flync_src_root: Path,
    feedback: Optional[str] = None,
    max_retries: int = 2,
    submodels_actually_linked: Optional[bool] = None,
    resolved_via_rag: Optional[list[str]] = None,
) -> str:
    """
    Génère et valide le script LLM en 3 étapes croissantes :
      1. Syntaxe (compile()).
      2. Classes autorisées (AST, anti-hallucination / anti-shadowing).
      3. EXÉCUTION RÉELLE (subprocess, nouveau) -- la seule étape qui
         aurait attrapé un `sys.exit(0)` sans `import sys`.
    Lève LLMGenerationError si aucun code ne passe les 3 étapes après
    max_retries tentatives -- l'appelant (main) est responsable du repli
    sur le mode template.
    """
    from langchain_core.messages import HumanMessage, SystemMessage

    human_prompt = _construire_prompt_humain(
        scenario, matched_classes, validators_by_class, class_lookup,
        feedback, submodels_actually_linked, resolved_via_rag,
    )
    messages = [SystemMessage(content=_SYSTEM_PROMPT_LLM), HumanMessage(content=human_prompt)]
    allowed_names = _classes_potentiellement_necessaires(matched_classes, class_lookup)

    last_error = "aucune tentative effectuée"
    for attempt in range(1, max_retries + 2):
        try:
            response = llm.invoke(messages)
        except Exception as exc:
            # Un appel LLM qui lève (429 rate-limit, timeout, erreur réseau...)
            # remontait auparavant tel quel jusqu'au ThreadPoolExecutor
            # (main(), except Exception generique), qui abandonnait le
            # scénario SANS AUCUN script écrit -- ni succès ni échec, juste
            # disparu (scenario_count != script_count, aucune trace pour
            # l'utilisateur). RoundRobinChat change de clé API à CHAQUE
            # appel (voir commun.py) précisément pour qu'une clé rate-limited
            # ne bloque pas l'agent -- mais ça ne sert à rien tant que rien
            # ne retente l'appel. On consomme une tentative et on continue :
            # la prochaine invoke() utilisera une autre clé (voir
            # RoundRobinChat.invoke), qui a de bonnes chances de ne pas être
            # limitée puisque chaque clé a son propre quota (orgs séparées).
            last_error = f"appel LLM échoué : {exc}"
            print(f"[agent-dev] {scenario['id']}: appel LLM échoué (tentative {attempt}) -> {exc}")
            continue
        code = extraire_code_python(response.content)

        error = valider_syntaxe(code)
        error_kind = "syntaxe"
        if error is None:
            error = valider_classes_autorisees(code, allowed_names)
            error_kind = "classes hors périmètre / shadowing"
        if error is None:
            exec_result = execute_generated_script(code, flync_src_root)
            if not exec_result.success:
                error = _format_execution_error(exec_result)
                error_kind = "exécution réelle"
        if error is None:
            return code

        last_error = error
        print(f"[agent-dev] {scenario['id']}: {error_kind} invalide (tentative {attempt}) -> {error}")
        messages.append(response)
        messages.append(HumanMessage(content=(
            f"Le code précédent est rejeté ({error_kind}) : {error}\n"
            f"Renvoie UNIQUEMENT le code Python corrigé, sous forme d'un unique "
            f"bloc ```python, en commençant par `import sys`, sans aucun texte "
            f"hors du code, sans commentaire."
        )))

    raise LLMGenerationError(
        f"{scenario['id']}: échec de génération LLM après {max_retries + 1} tentative(s) -- {last_error}"
    )


# ---------------------------------------------------------------------------
# Agent Maître : classification (nouveau, 0 appel LLM)
# ---------------------------------------------------------------------------

@dataclass
class ScenarioClassification:
    """Résultat de l'Agent Maître de classification pour un scénario."""
    scenario: dict
    verdict: object  # ScenarioVerdict
    category: str  # "MONO_MODULE" | "CROSS_MODULE" | "REQUIRES_SDK" | "UNRESOLVED"


def classify_all_scenarios(
    scenarios: list[dict],
    kb_index: KBIndex,
    class_lookup: dict[str, ClassInfo],
    relation_graph,
    retriever: Optional[object],
) -> list[ScenarioClassification]:
    """
    Agent Maître (classification) : passe en revue TOUS les scénarios AVANT
    toute génération, sans aucun appel LLM (verify_scenario est purement
    local : matching de nom + repli RAG TF-IDF + lecture du graphe de
    dépendances -- rapide même sur des centaines de scénarios).

    Distingue quatre catégories :
      - MONO_MODULE  : un seul sous-module déclaré, au moins une entité résolue.
      - CROSS_MODULE : 2+ sous-modules déclarés (scénario "cross_module(...)").
      - REQUIRES_SDK : entité(s) trouvée(s) uniquement dans le SDK.
      - UNRESOLVED   : aucune entité résolue, ni matching exact ni RAG.

    Le verdict est calculé UNE SEULE FOIS ici et transmis tel quel aux
    agents esclaves (_process_one_classified_scenario) : pas de second
    appel à verify_scenario lors de la génération.
    """
    classifications: list[ScenarioClassification] = []
    for scenario in scenarios:
        verdict = verify_scenario(scenario, kb_index, class_lookup, relation_graph, retriever)

        if verdict.classification == "REQUIRES_SDK":
            category = "REQUIRES_SDK"
        elif verdict.classification == "UNRESOLVED":
            category = "UNRESOLVED"
        elif len(verdict.submodels_declared) >= 2:
            category = "CROSS_MODULE"
        else:
            category = "MONO_MODULE"

        classifications.append(ScenarioClassification(scenario=scenario, verdict=verdict, category=category))
    return classifications


def _print_classification_report(classifications: list[ScenarioClassification], mode: str) -> None:
    """Rapport de l'Agent Maître, affiché avant toute génération."""
    counts: dict[str, int] = {}
    for c in classifications:
        counts[c.category] = counts.get(c.category, 0) + 1

    print("\n[agent-maitre] ===== Rapport de classification (0 appel LLM) =====")
    for category in ("MONO_MODULE", "CROSS_MODULE", "REQUIRES_SDK", "UNRESOLVED"):
        print(f"[agent-maitre]   {category:14s} : {counts.get(category, 0)}")

    cross = [c for c in classifications if c.category == "CROSS_MODULE"]
    suspects = [c for c in cross if c.verdict.submodels_actually_linked is False]
    if suspects:
        print(f"[agent-maitre]   ⚠️  {len(suspects)}/{len(cross)} scénario(s) cross-module SANS "
              f"couplage AST réel trouvé : {', '.join(c.scenario['id'] for c in suspects)}")

    if cross and mode == "template":
        print(f"[agent-maitre]   ⚠️  ATTENTION : {len(cross)} scénario(s) cross-module vont être "
              f"générés en --mode template, qui NE PEUT PAS modéliser de relation entre objets "
              f"(limitation structurelle). Ces scripts seront syntaxiquement valides mais très "
              f"probablement incomplets vis-à-vis de la relation métier attendue. "
              f"Utilise --mode llm pour ces scénarios.")

    print("[agent-maitre] " + "=" * 58 + "\n")


# ---------------------------------------------------------------------------
# Traitement d'un scénario (unité de parallélisation -- Agents Esclaves)
# ---------------------------------------------------------------------------

def _resolve_matched_classes(verdict, class_lookup: dict[str, ClassInfo]) -> list[ClassInfo]:
    matched = []
    for name in verdict.entities_found_in_model:
        ci = class_lookup.get(name)
        if ci is None:
            print(f"[agent-dev] AVERTISSEMENT: {verdict.scenario_id}: entité '{name}' "
                  f"trouvée par le Vérificateur mais absente de class_lookup -- ignorée.")
            continue
        if ci.is_enum:
            print(f"[agent-dev] INFO: {verdict.scenario_id}: '{name}' est un Enum -- "
                  f"pas instancié directement.")
            continue
        matched.append(ci)
    return matched


@dataclass
class ScenarioProcessingResult:
    scenario_id: str
    classification: str
    n_matched_classes: int
    out_path: Optional[Path]
    execution_success: Optional[bool]
    error: Optional[str] = None


def _output_path_for(classification: "ScenarioClassification", output_dir: Path) -> Path:
    """
    Détermine le chemin de sortie d'un script généré.

    Organisation choisie : un sous-dossier par CATÉGORIE (mono_module/
    cross_module/requires_sdk/unresolved) -- c'est l'axe qui compte le plus
    pour la relecture, car un script cross-module peut s'exécuter avec
    succès (exit 0) tout en étant sémantiquement faux (relation non
    modélisée, cf. SC-CROSS-001) : ce bug-là est INVISIBLE à l'exécution,
    contrairement à Positive/Negative qui se prouve déjà par le code de
    sortie et le contenu du stdout ("SUCCESS" vs "EXPECTED ERROR"). Grouper
    physiquement les scripts cross-module permet de cibler la relecture
    manuelle là où l'automatique (exécution réelle) ne suffit pas.

    Positive/Negative (scenario['type']) reste visible en SUFFIXE du nom de
    fichier -- information non déductible du seul ID de scénario (les IDs
    KPIT type SC-APP-001 ne l'encodent pas), donc utile à garder visible
    sans ouvrir le fichier, mais qui ne justifie pas une arborescence à part
    puisqu'elle n'a pas le même besoin de relecture ciblée.
    """
    category_dir = output_dir / classification.category.lower()
    category_dir.mkdir(parents=True, exist_ok=True)
    func_id = re.sub(r"[^a-z0-9_]", "_", classification.scenario["id"].lower())
    type_suffix = classification.scenario.get("type", "unknown").lower()
    return category_dir / f"script_{func_id}_{type_suffix}.py"


def _process_one_classified_scenario(
    classification: "ScenarioClassification",
    class_lookup: dict[str, ClassInfo],
    mode: str,
    llm_by_category: Optional[dict],
    flync_src_root: Path,
    output_dir: Path,
    llm_max_retries: int,
) -> ScenarioProcessingResult:
    """
    Agent Esclave : traite un scénario DÉJÀ classifié par l'Agent Maître
    (classify_all_scenarios) -- génération -> exécution réelle -> écriture
    sur disque. Ne recalcule jamais verify_scenario() (déjà fait en amont,
    une seule fois, par le Maître). Fonction pure du point de vue de
    l'appelant : c'est ce qui permet de la distribuer sur un
    ThreadPoolExecutor sans verrou.
    """
    scenario = classification.scenario
    verdict = classification.verdict
    matched_classes = _resolve_matched_classes(verdict, class_lookup)
    validators_by_class = verdict.validators_on_matched_classes

    if classification.category == "REQUIRES_SDK":
        content = (
            "import sys\n\n"
            'print("ERROR: scenario requires SDK, out of current KB scope")\n'
            "sys.exit(1)\n"
        )
        exec_success: Optional[bool] = None
    elif mode == "template":
        if classification.category == "CROSS_MODULE":
            print(f"[agent-dev] {scenario['id']}: cross-module en mode template -- "
                  f"relation NON modélisée (limitation structurelle, voir rapport de "
                  f"classification). Script généré quand même, à relire manuellement.")
        content, warnings = generate_construction_script(
            scenario, matched_classes, validators_by_class, class_lookup,
            submodels_actually_linked=verdict.submodels_actually_linked,
        )
        for w in warnings:
            print(f"[agent-dev] AVERTISSEMENT: {w}")
        # Exécution réelle même en mode template : la génération est
        # déterministe (pas de retry possible), mais on ne suppose plus
        # silencieusement que le script fonctionne -- on le prouve. Notez
        # que "exécution OK" ne prouve PAS la relation cross-module (voir
        # docstring de _output_path_for) : seulement l'absence d'erreur.
        exec_result = execute_generated_script(content, flync_src_root)
        exec_success = exec_result.success
        if not exec_result.success:
            print(f"[agent-dev] {scenario['id']}: ÉCHEC D'EXÉCUTION (mode template, "
                  f"pas de retry) -> {_format_execution_error(exec_result)}")
    else:
        llm = llm_by_category[classification.category] if classification.category in llm_by_category \
            else llm_by_category["MONO_MODULE"]
        try:
            content = generate_llm_script(
                scenario, matched_classes, validators_by_class, class_lookup, llm,
                flync_src_root, max_retries=llm_max_retries,
                submodels_actually_linked=verdict.submodels_actually_linked,
                resolved_via_rag=verdict.resolved_via_rag,
            )
            exec_success = True  # generate_llm_script ne retourne qu'un code déjà exécuté avec succès
        except LLMGenerationError as exc:
            print(f"[agent-dev] {exc} -> repli sur le mode template pour ce scénario.")
            content, warnings = generate_construction_script(
                scenario, matched_classes, validators_by_class, class_lookup,
                submodels_actually_linked=verdict.submodels_actually_linked,
            )
            for w in warnings:
                print(f"[agent-dev] AVERTISSEMENT: {w}")
            exec_result = execute_generated_script(content, flync_src_root)
            exec_success = exec_result.success

    out_path = _output_path_for(classification, output_dir)
    out_path.write_text(content, encoding="utf-8")

    return ScenarioProcessingResult(
        scenario_id=scenario["id"],
        classification=verdict.classification,
        n_matched_classes=len(matched_classes),
        out_path=out_path,
        execution_success=exec_success,
    )


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Développeur Python — génère les scripts de construction.")
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--mode", choices=["template", "llm"], default="template")
    parser.add_argument("--llm-backend", choices=["ollama", "anthropic", "gemini", "groq"], default=None)
    parser.add_argument("--llm-max-retries", type=int, default=2)
    parser.add_argument("--output-dir", default="./generated_scripts")
    parser.add_argument("--max-workers", type=int, default=4,
                         help="Nombre de scénarios traités en parallèle (défaut: 4).")
    args = parser.parse_args()

    scenarios_data = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
    scenarios = scenarios_data["scenarios"]

    print("[agent-dev] Analyse de la KB via l'Agent Lecteur/Analyste ...")
    agent = AgentLecteurAnalyste(FLYNC_KB)
    full_report = agent.run()

    class_lookup: dict[str, ClassInfo] = full_report.build_class_lookup()
    flync_src_root = agent.repo_dir / "src"

    kb_index = KBIndex(agent.repo_dir)
    kb_index.build_from_model(agent, full_report)
    kb_index.build_from_sdk()

    relation_graph = build_module_relation_graph(full_report)
    print(f"[agent-dev] Graphe de relations inter-modules : {relation_graph.total_edges} lien(s), "
          f"{len(relation_graph.bridge_class_index)} classe(s)-pont.")

    retriever = None
    try:
        from phase2.src.flync_pipeline.kb_retriever import HybridKBRetriever
        retriever = HybridKBRetriever()
        retriever.index_classes(list(class_lookup.values()))
        print(f"[agent-dev] Repli RAG actif ({retriever.indexed_class_count} classe(s) indexée(s)).")
    except ImportError as exc:
        print(f"[agent-dev] Repli RAG désactivé (dépendance manquante: {exc}).")

    # Deux modeles Groq distincts : qwen3.8-27b (rapide) pour MONO_MODULE
    # (le gros du volume, une seule classe a instancier), gpt-oss-120b
    # (raisonnement plus fort) pour CROSS_MODULE (doit modeliser une vraie
    # relation entre plusieurs classes). Construits une seule fois ici,
    # puis choisis par categorie dans _process_one_classified_scenario --
    # pas de reconstruction de client par scenario.
    llm_by_category = {
        "MONO_MODULE": get_llm(args.llm_backend, category="MONO_MODULE"),
        "CROSS_MODULE": get_llm(args.llm_backend, category="CROSS_MODULE"),
    } if args.mode == "llm" else None

    print("[agent-maitre] Classification de tous les scénarios (0 appel LLM)...")
    classifications = classify_all_scenarios(scenarios, kb_index, class_lookup, relation_graph, retriever)
    _print_classification_report(classifications, args.mode)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    results: list[ScenarioProcessingResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_classification = {
            executor.submit(
                _process_one_classified_scenario,
                classification, class_lookup, args.mode, llm_by_category, flync_src_root,
                output_dir, args.llm_max_retries,
            ): classification
            for classification in classifications
        }
        for future in concurrent.futures.as_completed(future_to_classification):
            classification = future_to_classification[future]
            try:
                result = future.result()
                results.append(result)
                status = (
                    "N/A" if result.execution_success is None
                    else ("OK" if result.execution_success else "ÉCHEC EXÉCUTION")
                )
                print(f"[agent-dev] {result.scenario_id} ({classification.category}, "
                      f"{result.n_matched_classes} classe(s), exécution={status}) -> {result.out_path}")
            except Exception as exc:
                scenario_id = classification.scenario["id"]
                print(f"[agent-dev] ERREUR CRITIQUE sur {scenario_id}: {exc}")
                # Still write a script (out_path=None used to mean this
                # scenario just vanished -- excluded from
                # results_by_script, no file on disk, no trace anywhere
                # downstream, while scenario_count kept counting it -- a
                # silent scenario_count/script_count mismatch with nothing
                # to show for it). Same visibility principle as the
                # REQUIRES_SDK placeholder above: a genuine, unexpected
                # failure should be a visible "Failed" script, not nothing.
                error_dir = output_dir / "generation_failed"
                error_dir.mkdir(parents=True, exist_ok=True)
                func_id = re.sub(r"[^a-z0-9_]", "_", scenario_id.lower())
                type_suffix = str(classification.scenario.get("type", "unknown")).lower()
                out_path = error_dir / f"script_{func_id}_{type_suffix}.py"
                out_path.write_text(
                    "import sys\n\n"
                    f"# GENERATION_FAILED: {scenario_id}\n"
                    f"# {exc}\n"
                    "print(\"GENERATION_FAILED: see comment above for the real error\")\n"
                    "sys.exit(1)\n",
                    encoding="utf-8",
                )
                results.append(ScenarioProcessingResult(
                    scenario_id=scenario_id, classification="ERROR",
                    n_matched_classes=0, out_path=out_path, execution_success=False, error=str(exc),
                ))

    n_exec_ok = sum(1 for r in results if r.execution_success is True)
    n_exec_fail = sum(1 for r in results if r.execution_success is False)
    n_exec_na = sum(1 for r in results if r.execution_success is None)
    print(f"\n[agent-dev] Terminé. {len(results)} scénario(s) -> {output_dir}")
    print(f"[agent-dev] Exécution réelle : {n_exec_ok} OK, {n_exec_fail} échec(s), {n_exec_na} N/A (REQUIRES_SDK).")

    # Resume machine-lisible, par script -- sans ca, phase2_service.run_phase2()
    # n'a que le code de sortie GLOBAL du process pour deviner
    # execution_success de CHAQUE script, et marque donc TOUT le lot comme
    # "failed" des qu'UN SEUL scenario echoue (meme les scripts qui ont
    # reellement reussi). Cle = nom de fichier sans extension (out_path.stem),
    # ce que phase2_service lit deja via Path(...).stem pour chaque script.
    results_by_script = {
        r.out_path.stem: r.execution_success
        for r in results if r.out_path is not None
    }
    (output_dir / "_results.json").write_text(
        json.dumps(results_by_script, indent=2), encoding="utf-8"
    )

    return 0 if n_exec_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
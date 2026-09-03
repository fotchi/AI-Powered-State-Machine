#!/usr/bin/env python3
"""
agent_developpeur.py
======================
Agent Développeur Python — dernier maillon du pipeline (§4 du cahier des
charges). Prend en entrée les scénarios KPIT + le verdict de l'Agent
Vérificateur (`scenario_verifier.py`), et produit des SCRIPTS PYTHON
AUTONOMES qui construisent le(s) objet(s) réel(s) du scénario — PAS des
tests pytest.

SUPPORT MULTI-CLASSES (scénarios cross-module)
------------------------------------------------
`verify_scenario()` (scenario_verifier.py) peut trouver PLUSIEURS classes
pertinentes pour un même scénario -- typiquement pour les scénarios
`cross_module(...)` qui touchent 2+ sous-modèles à la fois (ex:
SC-CROSS-001 : un CANFrameForwarder ET un EthSocketEgress). Dans ce cas,
l'Agent Développeur construit TOUTES les classes trouvées dans le MÊME
script, avec un import par classe -- ce n'est jamais tronqué à la première
entité trouvée.

CONTRAT DE SORTIE (exit code)
------------------------------
  * Scénarios Positive :
      - instanciation directe de TOUS les objets réels, SANS try/except ;
      - si tout se passe bien -> `print("SUCCESS")` puis `sys.exit(0)` ;
      - toute exception imprévue fait planter le script naturellement,
        avec un exit code != 0 (FAIL).

  * Scénarios Negative :
      - instanciation de TOUS les objets à l'intérieur d'un même bloc
        `try/except ValidationError as exc` (le scénario ne précise pas
        toujours quel objet porte la faute injectée -- le bloc try couvre
        donc l'ensemble de la construction) ;
      - `ValidationError` levée -> `print(f"EXPECTED ERROR: {exc}")` puis
        `sys.exit(0)` (PASS) ;
      - toute autre exception -> `print(f"UNEXPECTED ERROR: ...")` puis
        `sys.exit(1)` (FAIL) ;
      - aucune exception levée -> `print("ERROR: expected ValidationError
        but no error was raised")` puis `sys.exit(1)` (FAIL).

Il n'existe plus que deux types de scénarios : Positive et Negative
(l'abstraction "Boundary" a été supprimée -- un cas limite est un cas
Negative comme un autre, avec sa propre faute injectée).

AUCUN COMMENTAIRE DANS LES SCRIPTS GÉNÉRÉS
--------------------------------------------
Ni le mode template ni le mode LLM n'écrivent de commentaire (`#`) ou de
docstring dans le fichier produit : uniquement du code Python exécutable.
Les informations utiles (champs non résolus, entités cross-module
ignorées, gaps de validators) sont affichées sur la console pendant la
génération, jamais injectées dans le script.

ROBUSTESSE MODE LLM
--------------------
Un petit modèle local (ex: llama3.1 via Ollama) répond parfois avec du
texte explicatif mélangé au code, ce qui casse la syntaxe. Pour ne jamais
laisser une telle réponse faire planter tout le pipeline :
  1. extraction robuste du code (`extraire_code_python`) ;
  2. validation avec `compile()` (`valider_syntaxe`) ;
  3. en cas d'échec, on renvoie l'erreur au LLM et on retente
     (--llm-max-retries, 2 par défaut) ;
  4. si ça échoue encore, repli automatique sur le mode template pour CE
     scénario uniquement (`LLMGenerationError` capturée dans `main()`).

DEUX MODES :
  --mode template (par défaut) : génération déterministe, sans LLM.
  --mode llm : LLM (Ollama local par défaut, sinon Anthropic/Gemini selon
      les clés disponibles). Aucun mode mock : si rien n'est disponible,
      erreur explicite plutôt que script factice.

USAGE :
    python agent_developpeur.py --scenarios kpit_scenarios.json \
        --mode template --output-dir generated_scripts

    python agent_developpeur.py --scenarios kpit_scenarios.json \
        --mode llm --output-dir generated_scripts
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Optional

from flync_pipeline.etape2_lecteur.agent_lecteur_analyste import AgentLecteurAnalyste, ClassInfo, FieldInfo
from flync_pipeline.etape1_discovery.kb_pointers import FLYNC_KB
from flync_pipeline.etape2_lecteur.module_relations import build_module_relation_graph
from flync_pipeline.etape3_verificateur.scenario_verifier import KBIndex, resolve_submodel_field, verify_scenario


class LLMGenerationError(RuntimeError):
    """Levée quand le LLM n'a pas réussi à produire un script Python
    syntaxiquement valide après --llm-max-retries tentatives."""


# ---------------------------------------------------------------------------
# Inference de valeurs placeholder
# ---------------------------------------------------------------------------

_ANNOTATED_RE = re.compile(r"^Annotated\[\s*([^,]+?)\s*,")
_MAX_NESTED_DEPTH = 3  # garde-fou anti-recursion infinie (classes qui se referencent en cycle)


def infer_placeholder(
    field_info: FieldInfo,
    class_lookup: dict[str, ClassInfo],
    _depth: int = 0,
    _visited: Optional[frozenset[str]] = None,
    _referenced_classes: Optional[set[str]] = None,
) -> tuple[str, bool]:
    """Retourne (valeur, resolu). `resolu=False` = type non inféré
    automatiquement (valeur de repli 'None'), à signaler en console par
    l'appelant -- jamais en commentaire dans le script.

    GERE TROIS CAS AU-DELA DES TYPES PRIMITIFS :
      1. `Annotated[X, ...]` (ex: `Annotated[str, Reference(...)]`) -- le
         wrapper Annotated est transparent : on infere sur le type interne
         X, la métadonnée (Reference(...) etc.) est ignorée pour la
         construction (elle ne change pas la forme de la valeur attendue).
      2. Le type reference une autre classe FLYNC connue dans class_lookup
         qui est un Enum -- on REFERENCE un de ses membres
         (`ClassName.MEMBRE`), on ne l'instancie jamais comme un modele.
      3. Le type reference une autre classe FLYNC connue qui est un modele
         Pydantic -- construction imbriquee recursive inline
         (`ClassName(sous_champ=...)`), plutot que d'abandonner sur `None`.
         Profondeur limitee a `_MAX_NESTED_DEPTH` et `_visited` empeche les
         cycles (classe qui se reference elle-meme, directement ou non)."""
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
            return "None", False  # Enum detecte mais aucun membre extrait -- non resolu

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
    """Fusionne les champs propres a la classe avec ceux herites de ses
    classes de base (recursivement), tant que la base est connue dans
    class_lookup (les bases externes type FLYNCBaseModel/BaseModel/
    RootModel s'arretent naturellement la)."""
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
    """CANFrameForwarder -> can_frame_forwarder (snake_case complet, plus
    lisible que la simple minuscule de la premiere lettre qui produisait
    des noms comme 'cANFrameForwarder' pour les acronymes en tete de nom)."""
    s = re.sub(r"(?<!^)(?<![A-Z])(?=[A-Z])", "_", class_info.name)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    return s.lower()


def build_construction_snippet(
    class_info: ClassInfo,
    class_lookup: dict[str, ClassInfo],
    indent: str = "",
    referenced_classes: Optional[set[str]] = None,
) -> tuple[list[str], list[str]]:
    """Retourne (lignes_de_code, avertissements) pour UNE classe. Les
    avertissements ne sont jamais écrits dans le script.

    `referenced_classes`, si fourni, est enrichi (mutation in-place) avec le
    nom de toute classe FLYNC référencée en profondeur (Enum ou modèle
    imbriqué) par les valeurs des champs -- l'appelant (generate_construction_script)
    s'en sert pour générer les imports supplémentaires nécessaires, sans
    quoi une valeur comme `SignalDataType.UINT8` provoquerait un
    `NameError` à l'exécution faute d'import."""
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


# ---------------------------------------------------------------------------
# Génération TEMPLATE (déterministe, sans LLM)
# ---------------------------------------------------------------------------

def generate_construction_script(
    scenario: dict,
    matched_classes: list[ClassInfo],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
    submodels_actually_linked: Optional[bool] = None,
) -> tuple[str, list[str]]:
    """Retourne (contenu_script, avertissements_console). Construit TOUTES
    les classes de `matched_classes` dans le même script (multi-classes
    pour les scénarios cross-module).

    `submodels_actually_linked` (cf. ScenarioVerdict.submodels_actually_linked
    dans scenario_verifier.py) : pour un scénario cross_module(A+B,...),
    indique si un couplage AST RÉEL (cross_module_imports) a été trouvé
    entre les modules déclarés. `False` signale un scénario potentiellement
    mal étiqueté par KPIT : les classes construites existent bien chacune
    dans leur module, mais rien dans le code ne les relie -- le script
    généré n'a alors aucune garantie de tester une VRAIE interaction
    cross-module, juste deux objets indépendants côte à côte."""
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
                f"réel (import croisé AST) trouvé entre les modules déclarés. Les classes "
                f"construites ci-dessous existent chacune dans leur module, mais rien dans le "
                f"code ne les relie : ce script teste deux objets indépendants, pas une vraie "
                f"interaction cross-module. Vérifier l'étiquetage 'submodel' de ce scénario KPIT "
                f"ou l'existence réelle du couplage attendu dans le code FLYNC."
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

    # -- imports : classes principales + classes referencees en profondeur
    # (Enum ou modele imbrique) par les valeurs de champs -- sans quoi une
    # valeur comme SignalDataType.UINT8 provoquerait un NameError faute
    # d'import (bug reel corrige ici).
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


# ---------------------------------------------------------------------------
# Extraction et validation du code produit par le LLM
# ---------------------------------------------------------------------------

_CODE_FENCE_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extraire_code_python(text: str) -> str:
    """Extrait le code Python d'une réponse LLM quelle que soit sa forme :
    un ou plusieurs blocs ```python ... ``` avec prose autour (on garde le
    plus long), ou aucun bloc du tout (texte brut renvoyé tel quel, la
    validation de syntaxe en aval tranchera)."""
    blocks = _CODE_FENCE_RE.findall(text)
    if blocks:
        return max(blocks, key=len).strip()
    return text.strip()


def valider_syntaxe(code: str) -> Optional[str]:
    """None si `code` est un module Python syntaxiquement valide, sinon un
    message d'erreur."""
    try:
        compile(code, "<generated>", "exec")
        return None
    except SyntaxError as exc:
        return f"{type(exc).__name__}: {exc}"


def _classes_potentiellement_necessaires(
    matched_classes: list[ClassInfo], class_lookup: dict[str, ClassInfo]
) -> set[str]:
    """Ensemble des noms de classes qu'un script LLM peut légitimement
    importer/utiliser pour CE scénario : les classes principales fournies
    au prompt, plus toute classe FLYNC référencée en profondeur par leurs
    champs requis (Enum ou modèle imbriqué) -- même mécanisme que
    `infer_placeholder` en mode template, réutilisé ici pour définir le
    périmètre autorisé côté LLM."""
    allowed = {ci.name for ci in matched_classes}
    for ci in matched_classes:
        collected: set[str] = set()
        for f in resolve_all_fields(ci, class_lookup):
            if f.required:
                infer_placeholder(f, class_lookup, _referenced_classes=collected)
        allowed |= collected
    return allowed


def valider_classes_autorisees(code: str, allowed_names: set[str]) -> Optional[str]:
    """Détecte deux hallucinations réelles observées avec un LLM local peu
    respectueux des consignes (llama3.1) :

      1. SHADOWING -- le script importe une vraie classe FLYNC puis la
         redéfinit localement (`class AppBindings(BaseModel): ...` après
         `from flync.model... import AppBindings`). La redéfinition masque
         l'import : le script construit alors un faux modèle bidon qui
         accepte n'importe quoi, et ne teste RIEN de réel -- tout en
         passant silencieusement (exit 0, "SUCCESS"). `compile()` seul ne
         détecte jamais ce cas car le code est syntaxiquement valide.
      2. CLASSE HORS PÉRIMÈTRE -- le script importe et utilise une classe
         FLYNC qui n'a jamais été listée dans le prompt pour ce scénario
         (le LLM invente une classe plausible plutôt que d'utiliser celles
         fournies, ex: ServiceConsumerReference/ServiceProviderReference
         pour un scénario qui ne parle que d'AppBindings).

    Retourne None si rien de suspect n'est détecté, sinon un message
    d'erreur explicite (utilisé pour le feedback de retry au LLM)."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"{type(exc).__name__}: {exc}"

    imported_flync_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("flync.model."):
            for alias in node.names:
                imported_flync_names.add(alias.asname or alias.name)

    unauthorized = imported_flync_names - allowed_names
    if unauthorized:
        return (
            f"classe(s) FLYNC importée(s) hors du périmètre fourni pour ce scénario : "
            f"{', '.join(sorted(unauthorized))} (seules ces classes étaient autorisées : "
            f"{', '.join(sorted(allowed_names)) or '(aucune)'}). N'utilise QUE les classes "
            f"listées dans le prompt, n'en invente aucune autre."
        )

    class_defs = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    shadowed = class_defs & imported_flync_names
    if shadowed:
        return (
            f"classe(s) importée(s) redéfinie(s) localement (shadowing) : {', '.join(sorted(shadowed))}. "
            f"Une classe importée depuis flync.model NE DOIT JAMAIS être redéfinie par une nouvelle "
            f"déclaration `class {next(iter(shadowed))}(...)` dans le script : cela masque l'import réel "
            f"et fait tester un faux modèle bidon au lieu du vrai. Supprime cette redéfinition et utilise "
            f"directement la classe importée."
        )

    return None


# ---------------------------------------------------------------------------
# Génération LLM (optionnelle)
# ---------------------------------------------------------------------------

def get_llm(backend: Optional[str] = None):
    """Sélectionne le backend LLM disponible. Aucun mode mock : si rien
    n'est disponible, on lève une erreur explicite."""
    import os

    if backend == "ollama" or (backend is None and _ollama_reachable()):
        from langchain_ollama import ChatOllama
        model = os.environ.get("OLLAMA_MODEL", "llama3.1")
        print(f"[agent-dev] Ollama détecté en local -> ChatOllama(model='{model}'). "
              f"Aucune clé API nécessaire, tourne entièrement sur ta machine.")
        return ChatOllama(model=model, temperature=0)

    if backend == "anthropic" or (backend is None and os.environ.get("ANTHROPIC_API_KEY")):
        from langchain_anthropic import ChatAnthropic
        print("[agent-dev] ANTHROPIC_API_KEY trouvée -> ChatAnthropic réel.")
        return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

    if backend == "gemini" or (backend is None and (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))):
        from langchain_google_genai import ChatGoogleGenerativeAI
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        print("[agent-dev] GEMINI_API_KEY trouvée -> ChatGoogleGenerativeAI réel.")
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=key)

    raise RuntimeError(
        "[agent-dev] Aucun backend LLM disponible (ni Ollama local, ni "
        "ANTHROPIC_API_KEY, ni GEMINI_API_KEY/GOOGLE_API_KEY). Le mode mock a été "
        "supprimé : configure un backend ou relance avec --mode template."
    )


def _ollama_reachable(host: str = "http://localhost:11434") -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(f"{host}/api/tags", timeout=1)
        return True
    except Exception:
        return False


def appeler_llm(prompt: str, backend: Optional[str] = None) -> str:
    """Point d'appel LLM générique et réutilisable."""
    from langchain_core.messages import HumanMessage
    llm = get_llm(backend)
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def nettoyer_balises_markdown(text: str) -> str:
    """DEPRECIE : conserve uniquement pour compatibilite retro avec du code
    appelant existant. Redirige vers extraire_code_python(), plus robuste
    (gere la prose avant/apres les balises)."""
    return extraire_code_python(text)


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
    "CONTRAT D'EXIT CODE, STRICT :\n"
    "- Toujours `import sys` en premier, plus les imports Pydantic / FLYNC.\n"
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
"'NavigationApp' liée à 'hpc_controller1'), le script doit reproduire cette "
"relation RÉELLE si elle est représentable par les classes, champs, modèles "
"imbriqués ou mécanismes de validation fournis dans le CONSTRUCTION PLAN. "
"Ne construis pas uniquement l'objet principal en ignorant les autres "
"entités nécessaires à la relation.\n"
"    - Identifie toutes les entités explicitement citées dans le scénario.\n"
"    - Cherche dans les champs et types réels fournis comment ces entités "
"    sont reliées.\n"
"    - Si une classe disponible représente l'autre extrémité de la relation, "
"    construis également cette classe dans le même script.\n"
"    - Si la relation est portée par un champ de l'objet principal, renseigne "
"    ce champ avec la valeur exacte donnée dans le scénario.\n"
"    - Si plusieurs objets doivent être construits pour représenter la "
"    relation, construis-les tous.\n"
"    - N'invente JAMAIS un champ ou une relation simplement parce que le "
"    scénario la décrit : la relation doit être confirmée par les classes, "
"    champs, validators ou mécanismes réels fournis par le Vérificateur.\n"
"    - Si la relation décrite par le scénario n'est pas représentable avec "
"    les éléments disponibles, ne fabrique pas de liaison artificielle : "
"    construis uniquement ce qui est réellement représentable.\n"
"8. REPRODUCTION EXACTE DE LA FAUTE : pour un scénario Negative, la "
    "construction doit provoquer réellement la faute décrite selon le mécanisme Pydantic sous-jacent.\n"
    "9. VALIDATION DISPONIBLE UNIQUEMENT : ne suppose pas qu'une ValidationError sera "
    "levée si le mécanisme réel est absent des modèles fournis. Si la validation n'existe pas "
    "dans le code réel, n'invente rien et ne simule pas l'erreur.\n"
    "10. LE PLAN DE CONSTRUCTION FOURNI PAR LE VÉRIFICATEUR EST LA SOURCE "
    "DE VÉRITÉ ABSOLUE. Suis le CONSTRUCTION PLAN / FAULT REPRODUCTION PLAN à la lettre. "
    "N'invente aucun mécanisme de substitution si le plan signale une limitation de la KB.\n"
    "11. INTERDICTION DE MOCKING OU STRUCT LOCALES : il est strictement interdit "
    "de créer des classes locales, classes Meta, validators custom locaux ou stubs. "
    "Le script doit utiliser exclusivement les modèles importés du package FLYNC.\n"
    "12. REPRODUCTION GENERIQUE DES FAUTES NEGATIVE : pour TOUT scénario "
    "Negative, reproduis la faute décrite dans le scénario en utilisant "
    "UNIQUEMENT les mécanismes réels identifiés par le Vérificateur. Le "
    "mécanisme peut être une contrainte Pydantic locale, un validator, une "
    "relation entre plusieurs objets, une contrainte d'unicité, une référence, "
    "une contrainte inter-module ou tout autre mécanisme réel explicitement "
    "fourni dans le CONSTRUCTION PLAN / FAULT REPRODUCTION PLAN.\n"
    "13. SOURCE DE VERITE POUR LA FAUTE : ne déduis, n'invente et ne remplace "
    "JAMAIS le mécanisme de validation décrit par le scénario. Le "
    "CONSTRUCTION PLAN / FAULT REPRODUCTION PLAN fourni par le Vérificateur "
    "détermine exactement quels objets doivent être construits, quelles "
    "valeurs doivent être utilisées et comment la faute doit être déclenchée. "
    "Suis ce plan à la lettre.\n"
    "14. FAUTES LOCALES ET GLOBALES : distingue une faute portant sur un seul "
    "objet d'une faute nécessitant plusieurs objets ou plusieurs composants. "
    "Si le plan indique qu'une faute nécessite plusieurs objets, construis "
    "TOUS les objets requis dans le scénario. Ne suppose jamais qu'une simple "
    "instanciation suffit pour une contrainte globale.\n"
    "15. AUCUNE VALIDATION IMAGINAIRE : deux objets identiques, deux valeurs "
    "identiques ou une relation décrite dans le texte ne provoquent pas "
    "automatiquement une ValidationError. Une erreur ne doit être attendue "
    "que si le code FLYNC réel fourni par le Vérificateur contient un mécanisme "
    "capable de la déclencher.\n"
    "16. INTERDICTION DE SIMULATION : si le mécanisme réel n'existe pas dans "
    "les modèles, validators ou mécanismes explicitement fournis, ne crée "
    "aucune classe, Meta, validator, registre, dictionnaire, fonction ou autre "
    "logique locale pour simuler la faute. Utilise uniquement les éléments "
    "réels disponibles dans la KB.\n"
    "17. SCÉNARIOS CROSS-MODULE : lorsqu'un scénario concerne plusieurs "
    "sous-modèles FLYNC, traite-les comme un scénario unique et utilise "
    "TOUTES les classes explicitement fournies par le Vérificateur pour les "
    "modules concernés. Le script doit contenir les imports réels et les "
    "instanciations nécessaires pour chaque classe requise par le plan.\n"
    "18. RELATION CROSS-MODULE RÉELLE : pour un scénario cross-module, ne "
    "suppose jamais que la présence de deux classes dans deux sous-modèles "
    "implique automatiquement une relation entre elles. Une relation entre "
    "modules ne peut être utilisée que si elle est explicitement identifiée "
    "dans le CONSTRUCTION PLAN / FAULT REPRODUCTION PLAN ou dans les "
    "informations réelles fournies par le Vérificateur.\n"
    "19. CONSTRUCTION DE LA RELATION : si le Vérificateur identifie une "
    "relation réelle entre les modules, construis les objets dans le script "
    "en respectant exactement cette relation, avec les champs, références, "
    "types et valeurs réellement disponibles. N'invente aucun champ ou "
    "mécanisme de liaison.\n"
    "20. CROSS-MODULE SANS COUPLAGE RÉEL : si le Vérificateur indique qu'aucun "
    "couplage réel n'existe entre les modules concernés, construis uniquement "
    "les objets réels nécessaires de chaque module, indépendamment les uns "
    "des autres. N'ajoute aucune référence artificielle, aucun champ de "
    "liaison, aucun wrapper, aucune classe intermédiaire et aucune logique "
    "locale pour simuler une interaction entre les modules.\n"
    "21. CROSS-MODULE NEGATIVE : si un scénario cross-module est Negative, "
    "détermine si la faute concerne un seul objet, plusieurs objets ou la "
    "relation entre les modules. Construis exactement les objets et les "
    "relations indiqués dans le FAULT REPRODUCTION PLAN. La ValidationError "
    "ou toute autre erreur attendue ne doit être considérée comme valide que "
    "si le mécanisme réel fourni par le Vérificateur peut effectivement la "
    "déclencher.\n"
    "22. NOMBRE DE CLASSES : le nombre de classes à construire est déterminé "
    "par le Vérificateur et non par le nombre de sous-modèles mentionnés dans "
    "le texte du scénario. Un scénario cross-module peut nécessiter plusieurs "
    "classes dans un même module ou des classes imbriquées. Construis toutes "
    "les classes explicitement requises par le plan et aucune classe "
    "supplémentaire.\n"
)
 
 
def _construire_prompt_humain(
    scenario: dict,
    matched_classes: list[ClassInfo],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
    feedback: Optional[str],
    submodels_actually_linked: Optional[bool] = None,
) -> str:
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
            blocks.append(
                f"{ci.name} (module réel: {ci.module}, fichier: {ci.file})\n"
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
 
        f"ANALYSE DES ENTITÉS ET RELATIONS MÉTIER :\n"
        f"- Analyse toutes les entités explicitement mentionnées dans la "
        f"description et le résultat attendu.\n"
        f"- Ne te limite PAS à la première classe disponible.\n"
        f"- Si le scénario décrit une relation entre plusieurs entités, "
        f"identifie comment cette relation est réellement représentée dans "
        f"les champs, types, modèles imbriqués ou validators des classes "
        f"fournies ci-dessous.\n"
        f"- Si cette relation est réellement représentable, construis TOUS "
        f"les objets nécessaires pour la reproduire dans le script.\n"
        f"- Utilise les valeurs EXACTES données dans le scénario lorsque "
        f"elles sont disponibles.\n"
        f"- Pour une relation cross-module, utilise les classes des différents "
        f"modules uniquement si le Vérificateur les a fournies et si leur "
        f"relation réelle est confirmée par la KB.\n"
        f"- N'invente JAMAIS un champ, une classe, un validator ou une relation "
        f"qui n'existe pas dans les informations fournies.\n"
        f"- Si une relation décrite dans le scénario ne peut pas être "
        f"représentée avec les classes, champs et validators fournis, ne crée "
        f"aucune liaison artificielle : construis uniquement ce qui est "
        f"réellement représentable.\n\n"
 
        f"Imports réels à utiliser :\n{imports_hint}\n\n"
        f"Classe(s) disponible(s) ({len(matched_classes)}) :\n{classes_desc}\n\n"
 
        f"Rappel : réponds UNIQUEMENT avec un bloc ```python contenant le "
        f"script complet, sans aucun texte avant/après, sans commentaire "
        f"dans le code."
    )
    if len(matched_classes) > 1 and submodels_actually_linked is False:
        human += (
            "\n\nATTENTION : ce scénario est déclaré cross-module, mais aucun couplage réel "
            "(import croisé) n'a été trouvé entre les modules concernés dans le code FLYNC réel. "
            "N'invente donc AUCUNE relation artificielle entre ces objets (pas de champ qui "
            "référence l'un depuis l'autre s'il n'existe pas réellement) : construis chaque objet "
            "de façon indépendante, avec des valeurs plausibles, sans les lier entre eux."
        )
    if feedback:
        human += (
            "\n\nFEEDBACK D'UNE EXÉCUTION PRÉCÉDENTE (le script précédent a échoué en "
            "validation — corrige le script généré pour tenir compte de ce retour) :\n"
            f"{feedback}"
        )
    return human
 
 
def _classes_potentiellement_necessaires(
    matched_classes: list[ClassInfo],
    class_lookup: dict[str, ClassInfo],
) -> set[str]:
    """Ensemble des noms de classes que le LLM a le droit d'utiliser dans le
    script : les classes matchées elles-mêmes, leurs classes de base
    (transitives, car un champ hérité peut nécessiter la base), et les
    classes référencées par leurs champs (types imbriqués, y compris à
    l'intérieur d'un `Annotated[...]` ou d'un `List[...]`/`Optional[...]`).
    Sert de liste blanche pour `valider_classes_autorisees` -- empêche le
    LLM d'halluciner une classe plausible mais inexistante dans le plan
    fourni (règle 4 du system prompt)."""
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
 
 
# Identifiants Python/Pydantic génériques qui ne sont jamais des classes
# FLYNC mais qui apparaissent légitimement comme des appels dans un script
# généré (types builtins, exceptions standard, décorateurs Pydantic...).
_BUILTIN_ALLOWED_CALLS = {
    "str", "int", "float", "bool", "list", "dict", "set", "tuple", "bytes",
    "print", "sys", "Path", "ValidationError", "Field", "BaseModel",
    "IPvAnyAddress", "IPv4Address", "IPv6Address", "IPv4Network", "IPv6Network",
    "UUID", "Decimal", "Enum",
}
 
 
def valider_classes_autorisees(code: str, allowed_names: set[str]) -> Optional[str]:
    """Analyse statique (AST) du code généré par le LLM : rejette le script
    si (a) il redéfinit localement une classe FLYNC importée (shadowing,
    règle 4ter), ou (b) il instancie une classe qui n'appartient ni à la
    liste blanche fournie par le Vérificateur, ni aux types builtins usuels
    (règle 4 -- interdiction d'halluciner une classe plausible). Retourne
    un message d'erreur exploitable en feedback LLM, ou None si le code
    est conforme."""
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
                f"depuis le vrai module FLYNC -- interdit (règle 4ter, cela masquerait le "
                f"modèle réel et testerait une classe locale bidon)."
            )
 
    allowed = allowed_names | _BUILTIN_ALLOWED_CALLS | imported_names
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            call_name = node.func.id
            if call_name[0:1].isupper() and call_name not in allowed:
                return (
                    f"Le code instancie '{call_name}(...)', qui n'appartient ni aux classes "
                    f"fournies par le Vérificateur, ni à leurs types de champs imbriqués -- "
                    f"classe potentiellement inventée (règle 4). Classes autorisées : "
                    f"{', '.join(sorted(allowed_names)) or '(aucune)'}."
                )
 
    return None
 
 
def generate_llm_script(
    scenario: dict,
    matched_classes: list[ClassInfo],
    validators_by_class: dict[str, list[str]],
    class_lookup: dict[str, ClassInfo],
    llm,
    feedback: Optional[str] = None,
    max_retries: int = 2,
    submodels_actually_linked: Optional[bool] = None,
) -> str:
    """Génère et valide le script LLM. Lève LLMGenerationError si aucun code
    syntaxiquement valide n'a pu être obtenu -- l'appelant (main) est
    responsable du repli sur le mode template."""
    from langchain_core.messages import HumanMessage, SystemMessage
 
    human_prompt = _construire_prompt_humain(
        scenario, matched_classes, validators_by_class, class_lookup, feedback, submodels_actually_linked
    )
    messages = [SystemMessage(content=_SYSTEM_PROMPT_LLM), HumanMessage(content=human_prompt)]
    allowed_names = _classes_potentiellement_necessaires(matched_classes, class_lookup)
 
    last_error = "aucune tentative effectuée"
    for attempt in range(1, max_retries + 2):
        response = llm.invoke(messages)
        code = extraire_code_python(response.content)
 
        error = valider_syntaxe(code)
        error_kind = "syntaxe"
        if error is None:
            error = valider_classes_autorisees(code, allowed_names)
            error_kind = "classes hors périmètre / shadowing"
        if error is None:
            return code
 
        last_error = error
        print(f"[agent-dev] {scenario['id']}: {error_kind} invalide (tentative {attempt}) -> {error}")
        messages.append(response)
        messages.append(HumanMessage(content=(
            f"Le code précédent est rejeté : {error}\n"
            f"Renvoie UNIQUEMENT le code Python corrigé, sous forme d'un unique "
            f"bloc ```python, sans aucun texte hors du code, sans commentaire."
        )))
 
    raise LLMGenerationError(
        f"{scenario['id']}: échec de génération LLM après {max_retries + 1} tentative(s) -- {last_error}"
    )
 

# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def _resolve_matched_classes(verdict, class_lookup: dict[str, ClassInfo]) -> list[ClassInfo]:
    """Resout les entites du Verificateur en ClassInfo instanciables.

    Un Enum trouve par le Verificateur (ex: scenario dont le texte mentionne
    'SignalDataType') n'est PAS une classe qu'on instancie directement --
    on ne peut pas faire `SignalDataType(...)`, seulement le REFERENCER
    depuis un champ qui en a besoin (deja gere par infer_placeholder). Il
    est donc exclu ici de `matched_classes`, avec un message INFO (pas un
    avertissement -- ce n'est pas une erreur, juste une nature differente)."""
    matched = []
    for name in verdict.entities_found_in_model:
        ci = class_lookup.get(name)
        if ci is None:
            print(f"[agent-dev] AVERTISSEMENT: {verdict.scenario_id}: entité '{name}' "
                  f"trouvée par le Vérificateur mais absente de class_lookup -- ignorée.")
            continue
        if ci.is_enum:
            print(f"[agent-dev] INFO: {verdict.scenario_id}: '{name}' est un Enum -- "
                  f"pas instancié directement, référencé via ses membres si un champ "
                  f"d'une autre classe le requiert.")
            continue
        matched.append(ci)
    return matched


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Développeur Python — génère les scripts de construction.")
    parser.add_argument("--scenarios", required=True)
    parser.add_argument("--mode", choices=["template", "llm"], default="template")
    parser.add_argument("--llm-backend", choices=["ollama", "anthropic", "gemini"], default=None,
                         help="Force un backend LLM précis ; sinon auto-détection (Ollama local > clés API). "
                              "Aucun fallback mock : une erreur est levée si rien n'est disponible.")
    parser.add_argument("--llm-max-retries", type=int, default=2,
                         help="Relances au LLM en cas de code syntaxiquement invalide, avant repli "
                              "automatique sur le mode template (défaut: 2).")
    parser.add_argument("--output-dir", default="./generated_scripts")
    parser.add_argument("--feedback", default=None,
                         help="Chemin optionnel vers un fichier JSON {scenario_id: feedback_text} "
                              "issu d'une exécution précédente en échec.")
    args = parser.parse_args()

    scenarios_data = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
    scenarios = scenarios_data["scenarios"]

    feedback_by_id: dict[str, str] = {}
    if args.feedback:
        feedback_by_id = json.loads(Path(args.feedback).read_text(encoding="utf-8"))

    print("[agent-dev] Analyse de la KB via l'Agent Lecteur/Analyste ...")
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
    print(f"[agent-dev] Graphe de relations inter-modules : {relation_graph.total_edges} lien(s), "
          f"{len(relation_graph.bridge_class_index)} classe(s)-pont.")

    llm = get_llm(args.llm_backend) if args.mode == "llm" else None

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    for scenario in scenarios:
        verdict = verify_scenario(scenario, kb_index, class_lookup, relation_graph)
        matched_classes = _resolve_matched_classes(verdict, class_lookup)
        validators_by_class = verdict.validators_on_matched_classes
        feedback = feedback_by_id.get(scenario["id"])

        if verdict.classification == "REQUIRES_SDK":
            content = (
                "import sys\n\n"
                'print("ERROR: scenario requires SDK, out of current KB scope")\n'
                "sys.exit(1)\n"
            )
        elif args.mode == "template":
            content, warnings = generate_construction_script(
                scenario, matched_classes, validators_by_class, class_lookup,
                submodels_actually_linked=verdict.submodels_actually_linked,
            )
            for w in warnings:
                print(f"[agent-dev] AVERTISSEMENT: {w}")
        else:
            try:
                content = generate_llm_script(
                    scenario, matched_classes, validators_by_class, class_lookup, llm,
                    feedback, max_retries=args.llm_max_retries,
                    submodels_actually_linked=verdict.submodels_actually_linked,
                )
            except LLMGenerationError as exc:
                print(f"[agent-dev] {exc} -> repli sur le mode template pour ce scénario.")
                content, warnings = generate_construction_script(
                    scenario, matched_classes, validators_by_class, class_lookup,
                    submodels_actually_linked=verdict.submodels_actually_linked,
                )
                for w in warnings:
                    print(f"[agent-dev] AVERTISSEMENT: {w}")

        func_id = re.sub(r"[^a-z0-9_]", "_", scenario["id"].lower())
        out_path = output_dir / f"script_{func_id}.py"
        out_path.write_text(content, encoding="utf-8")
        print(f"[agent-dev] {scenario['id']} ({verdict.classification}, "
              f"{len(matched_classes)} classe(s)) -> {out_path}")

    print(f"\n[agent-dev] Terminé. Scripts dans {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
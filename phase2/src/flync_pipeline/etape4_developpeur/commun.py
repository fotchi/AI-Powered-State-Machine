
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from phase2.src.flync_pipeline.etape1_discovery.kb_pointers import FLYNC_KB
from phase2.src.flync_pipeline.etape2_lecteur.agent_lecteur_analyste import (
    AgentLecteurAnalyste,
    ClassInfo,
    KBAnalysisReport,
)
from phase2.src.flync_pipeline.etape2_lecteur.module_relations import (
    ModuleRelationGraph,
    build_module_relation_graph,
)
from phase2.src.flync_pipeline.etape3_verificateur.scenario_verifier import KBIndex

from dotenv import load_dotenv

# phase2 has no root .env of its own and its subprocess is launched with
# cwd=<repo root> (see backend/app/services/phase2_service.py), so a bare
# load_dotenv() would never find phase2/.env on its own -- load it explicitly.
load_dotenv(Path(__file__).resolve().parents[3] / ".env")


class LLMGenerationError(RuntimeError):
    """Levée quand le LLM n'a pas produit de script valide après N tentatives."""


DEFAULT_EXECUTION_TIMEOUT_SECONDS = 30
_MAX_FEEDBACK_CHARS = 2_000


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
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(flync_src_root) + (os.pathsep + existing if existing else "")

    try:
        completed = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True,
            timeout=timeout_seconds, env=env,
        )
        return ExecutionResult(
            success=completed.returncode == 0,
            stdout=completed.stdout, stderr=completed.stderr,
            returncode=completed.returncode, timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        return ExecutionResult(
            success=False, stdout=exc.stdout or "",
            stderr=f"Timeout dépassé ({timeout_seconds}s).",
            returncode=None, timed_out=True,
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def format_execution_error(exec_result: ExecutionResult) -> str:
    if exec_result.timed_out:
        return exec_result.stderr
    msg = (
        f"Le script s'est exécuté avec le code de sortie {exec_result.returncode} "
        f"(attendu: 0). stderr réel :\n{exec_result.stderr.strip()}\n"
        f"stdout réel :\n{exec_result.stdout.strip()}"
    )
    return msg[:_MAX_FEEDBACK_CHARS] + "\n...[tronqué]" if len(msg) > _MAX_FEEDBACK_CHARS else msg


_CODE_FENCE_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extraire_code_python(text: str) -> str:
    blocks = _CODE_FENCE_RE.findall(text)
    return max(blocks, key=len).strip() if blocks else text.strip()


def valider_syntaxe(code: str) -> Optional[str]:
    try:
        compile(code, "<generated>", "exec")
        return None
    except SyntaxError as exc:
        return f"{type(exc).__name__}: {exc}"


_BUILTIN_ALLOWED_CALLS = {
    "str", "int", "float", "bool", "list", "dict", "set", "tuple", "bytes",
    "print", "sys", "Path", "ValidationError", "Field", "BaseModel",
    "IPvAnyAddress", "IPv4Address", "IPv6Address", "IPv4Network", "IPv6Network",
    "UUID", "Decimal", "Enum",
}

_TYPE_NAME_RE = re.compile(r"[A-Z][A-Za-z0-9_]*")


def classes_potentiellement_necessaires(
    matched_classes: list[ClassInfo],
    class_lookup: dict[str, ClassInfo],
) -> set[str]:
    """[FIX-4] Enum inclus dans la liste blanche."""
    allowed: set[str] = set()
    seen: set[str] = set()

    def _walk(ci: ClassInfo) -> None:
        if ci.name in seen:
            return
        seen.add(ci.name)
        allowed.add(ci.name)
        for base in ci.bases:
            allowed.add(base)
            bi = class_lookup.get(base)
            if bi:
                _walk(bi)
        for f in ci.fields:
            for candidate in _TYPE_NAME_RE.findall(f.type_str):
                if candidate in class_lookup:
                    allowed.add(candidate)
                    _walk(class_lookup[candidate])

    for ci in matched_classes:
        _walk(ci)
    return allowed


def valider_classes_autorisees(code: str, allowed_names: set[str]) -> Optional[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"{type(exc).__name__}: {exc}"

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add((alias.asname or alias.name).split(".")[0])

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name in imported:
            return (
                f"Le code redéfinit localement '{node.name}' qui a été importé "
                f"depuis le vrai module FLYNC -- interdit."
            )

    allowed = allowed_names | _BUILTIN_ALLOWED_CALLS | imported
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name[0:1].isupper() and name not in allowed:
                return (
                    f"Le code instancie '{name}(...)', absent des classes fournies. "
                    f"Classes autorisées : {', '.join(sorted(allowed_names)) or '(aucune)'}."
                )
    return None

_ALWAYS_ALLOWED_SUBMODULES = frozenset({
    "flync_4_metadata", "flync_4_common", "flync_4_base", "flync_base",
})


def valider_imports_flync(
    code: str,
    known_modules: Optional[set[str]],
    class_lookup: Optional[dict[str, ClassInfo]] = None,
) -> Optional[str]:
   
    if known_modules is None:
        return None
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"{type(exc).__name__}: {exc}"

    class_locations: dict[str, tuple[str, str]] = {}
    if class_lookup:
        for ci in class_lookup.values():
            class_locations[ci.name] = (ci.module, ci.file.removesuffix(".py"))

    _NON_CLASS_SYMBOLS = frozenset({"ValidationError", "Field", "BaseModel"})

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        parts = module.split(".")
        if not (len(parts) >= 3 and parts[0] == "flync" and parts[1] == "model"):
            continue

        submod = parts[2]
        file_stem = parts[3] if len(parts) >= 4 else None

        if submod not in known_modules and submod not in _ALWAYS_ALLOWED_SUBMODULES:
            return (
                f"Import depuis un sous-module FLYNC inexistant : "
                f"'flync.model.{submod}' n'est pas dans la KB connue. "
                f"Sous-modules valides : {', '.join(sorted(known_modules))}. "
                f"Utilise uniquement les imports fournis dans le prompt."
            )

        if not class_lookup:
            continue

        for alias in node.names:
            sym = alias.name
            if sym in _NON_CLASS_SYMBOLS:
                continue
            loc = class_locations.get(sym)

            if loc is not None:
                real_mod, real_stem = loc
                # [2] Fichier ou sous-module incorrect
                if real_mod != submod or (file_stem and real_stem != file_stem):
                    file_stem_display = file_stem or "?"
                    return (
                        f"Import incorrect pour '{sym}' : "
                        f"la classe se trouve dans "
                        f"'flync.model.{real_mod}.{real_stem}', "
                        f"pas dans 'flync.model.{submod}.{file_stem_display}'. "
                        f"Utilise l'import exact fourni dans le prompt."
                    )
            else:
                    file_stem_sym = file_stem or "?"
                    return (
                        f"Symbole '{sym}' importé depuis "
                        f"'flync.model.{submod}.{file_stem_sym}' "
                        f"n'existe pas dans la KB FLYNC. "
                        f"N'importe jamais un nom de classe inventé."
                    )
    return None


def _resolve_all_fields_commun(
    ci: ClassInfo,
    class_lookup: dict[str, ClassInfo],
) -> list:
    """Résout les champs d'une classe avec héritage (version locale à commun.py
    pour éviter une dépendance circulaire avec agent_developpeur_mono.py)."""
    seen: set[str] = set()
    result: list = []

    def _walk(c: ClassInfo) -> None:
        for base in c.bases:
            bi = class_lookup.get(base)
            if bi:
                _walk(bi)
        for f in c.fields:
            if f.name not in seen:
                seen.add(f.name)
                result.append(f)

    _walk(ci)
    return result


def valider_kwargs_autorises(
    code: str,
    matched_classes: list[ClassInfo],
    class_lookup: dict[str, ClassInfo],
) -> Optional[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"{type(exc).__name__}: {exc}"

    legal_fields: dict[str, set[str]] = {}

    def _register(ci: ClassInfo) -> None:
        if ci.name in legal_fields:
            return
        legal_fields[ci.name] = {
            f.name for f in _resolve_all_fields_commun(ci, class_lookup)
        }
        for f in _resolve_all_fields_commun(ci, class_lookup):
            for candidate in _TYPE_NAME_RE.findall(f.type_str):
                ci2 = class_lookup.get(candidate)
                if ci2 and not ci2.is_enum:
                    _register(ci2)

    for ci in matched_classes:
        _register(ci)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name):
            continue
        cls_name = node.func.id
        if cls_name not in legal_fields:
            continue
        allowed = legal_fields[cls_name]
        for kw in node.keywords:
            if kw.arg is None:  # **kwargs spread — on ne peut pas vérifier
                continue
            if kw.arg not in allowed:
                return (
                    f"{cls_name}(...{kw.arg}=...) : '{kw.arg}' n'est pas un "
                    f"champ de {cls_name}. "
                    f"Champs autorisés : {', '.join(sorted(allowed)) or '(aucun)'}."
                )
    return None


def _collect_exit_codes(body: list[ast.stmt]) -> list[int]:
    """[FIX-1] Détecte sys.exit(N) ET exit(N) (bare) dans un corps AST."""
    codes: list[int] = []
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if not isinstance(node, ast.Call):
            continue
        arg0 = node.args[0] if node.args else None
        if not isinstance(arg0, ast.Constant) or not isinstance(arg0.value, int):
            continue
        func = node.func
        is_sys_exit = (
            isinstance(func, ast.Attribute) and func.attr == "exit"
            and isinstance(func.value, ast.Name) and func.value.id == "sys"
        )
        is_bare = isinstance(func, ast.Name) and func.id == "exit"
        if is_sys_exit or is_bare:
            codes.append(arg0.value)
    return codes


def valider_contrat_negative(code: str) -> Optional[str]:
    """[FIX-1][FIX-2] Valide le contrat try/except ValidationError/else."""
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"SyntaxError dans valider_contrat_negative : {exc}"

    has_ve = any(
        isinstance(n, ast.ImportFrom) and n.module == "pydantic"
        and any(a.name == "ValidationError" for a in n.names)
        for n in ast.walk(tree)
    )
    if not has_ve:
        return (
            "Script Negative sans `from pydantic import ValidationError` -- "
            "il ne peut pas distinguer un succès inattendu d'une faute capturée."
        )

    try_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Try)]
    if not try_nodes:
        return "Script Negative sans bloc try/except."

    for t in try_nodes:
        ve_handler: Optional[ast.ExceptHandler] = None
        for h in t.handlers:
            if h.type is None:
                continue
            names = (
                [h.type.id] if isinstance(h.type, ast.Name) else
                [e.id for e in h.type.elts if isinstance(e, ast.Name)]
                if isinstance(h.type, ast.Tuple) else []
            )
            if "ValidationError" in names:
                ve_handler = h
                break
        if ve_handler is None:
            continue

        if 0 in _collect_exit_codes(t.body):
            return (
                "Le bloc try contient sys.exit(0) sur le chemin de succès -- "
                "exit(0) ne doit se produire QUE dans except ValidationError."
            )
        orelse = getattr(t, "orelse", [])
        if orelse and 0 in _collect_exit_codes(orelse):
            return (
                "Le bloc else du try contient sys.exit(0) -- ce bloc s'exécute "
                "quand AUCUNE exception n'a été levée (chemin de succès). "
                "Déplacer sys.exit(0) dans le except ValidationError."
            )
        if 0 not in _collect_exit_codes(ve_handler.body):
            return (
                "Le except ValidationError ne contient pas sys.exit(0) -- "
                "le contrat d'exit code Negative n'est pas respecté."
            )
        return None

    return "Aucun `except ValidationError` trouvé dans les blocs try."



_VALUE_PATTERN = re.compile(
    r"(?:(?<=:\s)|(?<=:\t)|(?<=: ))(['\"]?)([a-zA-Z0-9_./:-]{2,})\1",
    re.MULTILINE,
)
_NUMERIC_RE = re.compile(r"^\d+(?:\.\d+)?$")
_SKIP_WORDS = frozenset({
    "true", "false", "null", "none", "yes", "no",
    "the", "an", "a", "is", "in", "of", "to", "for", "with", "and", "or",
})


def extract_scenario_values(scenario: dict) -> dict[str, Any]:
    """Extrait les paires clé/valeur explicites depuis description +
    injected_fault du scénario (heuristique simple basée sur les patterns
    YAML-like et les valeurs numériques mentionnées)."""
    values: dict[str, Any] = {}
    text = (scenario.get("description") or "") + " " + (scenario.get("injected_fault") or "")

    for m in re.finditer(
        r"\b([a-z][a-z0-9_]{1,40}):\s+(['\"]?)([^\s,'\"]{1,80})\2",
        text, re.IGNORECASE,
    ):
        key, val = m.group(1).lower(), m.group(3)
        if key not in _SKIP_WORDS and val not in _SKIP_WORDS:
            if _NUMERIC_RE.match(val):
                values[key] = float(val) if "." in val else int(val)
            else:
                values[key] = val

    return values


def format_scenario_values_block(values: dict[str, Any]) -> str:
    if not values:
        return (
            "VALEURS DU SCÉNARIO : (aucune valeur explicite détectée -- "
            "utilise des valeurs plausibles cohérentes avec la description)"
        )
    lines = [
        "VALEURS DU SCÉNARIO (à utiliser TELLES QUELLES dans le script généré) :"
    ]
    for k, v in values.items():
        lines.append(f"  {k} = {v!r}")
    lines.append(
        "Ces valeurs seront vérifiées automatiquement dans le code généré. "
        "Ne les remplace pas par des placeholders génériques."
    )
    return "\n".join(lines)


def check_orphan_scenario_values(
    scenario_values: dict[str, Any],
    known_field_names: set[str],
) -> list[str]:
    """Retourne les clés de scenario_values qui ne correspondent à aucun
    champ réel des classes résolues."""
    return [k for k in scenario_values if k not in known_field_names]


def valider_fidelite_valeurs(
    code: str,
    scenario_values: dict[str, Any],
    known_field_names: set[str],
) -> Optional[str]:
    """[FIX-10] Vérifie que les valeurs extraites du scénario et mappables
    à des champs réels sont bien présentes dans le code généré."""
    if not scenario_values:
        return None
    for key, val in scenario_values.items():
        if key not in known_field_names:
            continue
        val_str = str(val)
        if val_str not in code and repr(val) not in code:
            return (
                f"La valeur du scénario '{key}={val!r}' n'apparaît pas dans "
                f"le code généré. Le script s'exécute mais ignore une valeur "
                f"explicitement demandée -- utilise {val!r} pour '{key}'."
            )
    return None



_ISOLATION_IMPOSSIBLE_PATTERNS = [
    (re.compile(r"dupli(?:cat|qu)[a-z]*\s+(?:instance_id|identifier|id\b)", re.I),
     "duplicate identifier check requires full-model context"),
    (re.compile(r"already\s+(?:in\s+use|exist|taken)", re.I),
     "uniqueness constraint requires full-model context"),
    (re.compile(r"dangling\s+reference", re.I),
     "dangling reference check requires full-model context"),
    (re.compile(r"undefined\s+(?:service|provider|consumer)", re.I),
     "cross-reference check requires full-model context"),
    (re.compile(r"missing\s+(?:or\s+)?dangling", re.I),
     "cross-reference check requires full-model context"),
]


def is_scenario_isolation_impossible(scenario: dict) -> tuple[bool, str]:
    """Retourne (True, raison) si la faute décrite par le scénario est
    structurellement impossible à reproduire par instanciation isolée."""
    fault = (scenario.get("injected_fault") or "").lower()
    desc = (scenario.get("description") or "").lower()
    text = fault + " " + desc
    for pattern, reason in _ISOLATION_IMPOSSIBLE_PATTERNS:
        if pattern.search(text):
            return True, reason
    return False, ""



def _expand_nested_for_prompt(
    ci: ClassInfo,
    class_lookup: dict[str, ClassInfo],
    depth: int = 0,
    max_depth: int = 2,
    _seen: Optional[frozenset[str]] = None,
) -> list[str]:
    """Génère des lignes indentées décrivant les champs d'une classe,
    en expandant récursivement les types imbriqués connus."""
    if _seen is None:
        _seen = frozenset()
    if ci.name in _seen or depth > max_depth:
        return []
    _seen = _seen | {ci.name}
    indent = "  " * (depth + 1)
    lines: list[str] = []

    for f in _resolve_all_fields_commun(ci, class_lookup):
        raw_type = f.type_str.strip()
        inner = raw_type
        for wrapper in ("Optional[", "List[", "list["):
            if inner.startswith(wrapper):
                inner = inner[len(wrapper):].rstrip("]")
                break
        if inner.startswith("Annotated["):
            depth_a = 0
            for idx, ch in enumerate(inner[len("Annotated["):], len("Annotated[")):
                if ch in "[(" : depth_a += 1
                elif ch in "])": depth_a -= 1
                elif ch == "," and depth_a == 0:
                    inner = inner[len("Annotated["):idx].strip()
                    break

        constraint = ""
        if f.default_str and "Field(" in (f.default_str or ""):
            constraint = f"  ← contrainte: {f.default_str}"

        if inner.startswith("Literal["):
            vals = inner[len("Literal["):-1]
            lines.append(
                f"{indent}{f.name}: {raw_type} "
                f"[VALEUR EXACTE PARMI: {vals}]{constraint}"
            )
        else:
            nested_ci = class_lookup.get(inner)
            if nested_ci and not nested_ci.is_enum and nested_ci.name not in _seen:
                lines.append(
                    f"{indent}{f.name}: {raw_type} "
                    f"[MODÈLE IMBRIQUÉ → instancier avec {inner}(...)]{constraint}"
                )
                lines.extend(
                    _expand_nested_for_prompt(nested_ci, class_lookup, depth + 1, max_depth, _seen)
                )
            elif nested_ci and nested_ci.is_enum:
                members = ", ".join(nested_ci.enum_members) or "?"
                lines.append(
                    f"{indent}{f.name}: {raw_type} "
                    f"[ENUM → utiliser {inner}.MEMBER parmi: {members}]{constraint}"
                )
            else:
                req = "obligatoire" if f.required else "optionnel"
                lines.append(f"{indent}{f.name}: {raw_type} ({req}){constraint}")
    return lines


def build_field_allowlist_block(
    matched_classes: list[ClassInfo],
    class_lookup: dict[str, ClassInfo],
) -> str:
    if not matched_classes:
        return "CHAMPS AUTORISÉS : (aucune classe résolue)"
    lines: list[str] = [
        "CHAMPS AUTORISÉS (liste exhaustive avec structure imbriquée -- "
        "aucun autre champ n'existe sur ces classes) :"
    ]
    for ci in matched_classes:
        stem = ci.file.removesuffix(".py")
        lines.append(
            f"\n▶ {ci.name}  "
            f"[import: from flync.model.{ci.module}.{stem} import {ci.name}]"
        )
        lines.extend(_expand_nested_for_prompt(ci, class_lookup))

    lines.append(
        "\nRÈGLES ABSOLUES :\n"
        "  • Champs MODÈLE IMBRIQUÉ : TOUJOURS instanciés avec la classe indiquée, "
        "JAMAIS passés comme chaîne de caractères (ex: version='1.0' est INTERDIT, "
        "écrire BaseVersion(version='1.0')).\n"
        "  • Champs Literal : utiliser EXACTEMENT l'une des valeurs listées "
        "(respecter la casse -- 'ecu' ≠ 'ECU').\n"
        "  • Tout champ absent des listes ci-dessus est INEXISTANT et provoque "
        "extra_forbidden (exit 1)."
    )
    return "\n".join(lines)



def _ollama_reachable(host: str = "http://localhost:11434") -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(f"{host}/api/tags", timeout=1)
        return True
    except Exception:
        return False


class _OllamaMessage:
    def __init__(self, content: str):
        self.content = content


class OllamaDirectChat:
    def __init__(
        self, model: str,
        host: str = "http://localhost:11434",
        temperature: float = 0.0,
    ):
        self.model = model
        self.host = host.rstrip("/")
        self.temperature = temperature

    def invoke(self, messages) -> _OllamaMessage:
        import requests
        role_map = {"system": "system", "human": "user", "ai": "assistant"}
        payload = [
            {"role": role_map.get(getattr(m, "type", None), "user"), "content": m.content}
            for m in messages
        ]
        resp = requests.post(
            f"{self.host}/api/chat",
            json={"model": self.model, "messages": payload,
                  "stream": False, "options": {"temperature": self.temperature}},
            timeout=180,
        )
        resp.raise_for_status()
        return _OllamaMessage(resp.json()["message"]["content"])


def _load_multi_keys(multi_env_var: str, single_env_var: str) -> list[str]:
    multi = os.environ.get(multi_env_var)
    if multi:
        keys = [k.strip() for k in multi.split(",") if k.strip()]
        if keys:
            return keys
    single = os.environ.get(single_env_var)
    return [single] if single else []


class RoundRobinChat:
    """Cycles through several clients for the same provider (one per API
    key) so a single rate-limited key doesn't stall the agent. agent_developpeur.py
    processes scenarios with a ThreadPoolExecutor and shares one llm instance
    across workers, so the index increment needs a lock."""

    def __init__(self, clients: list, label: str):
        self._clients = clients
        self.label = label
        self._i = 0
        self._lock = threading.Lock()

    def invoke(self, messages):
        with self._lock:
            client = self._clients[self._i % len(self._clients)]
            self._i += 1
        return client.invoke(messages)


def get_llm(backend: Optional[str] = None, category: Optional[str] = None):
    """`category` ("MONO_MODULE" | "CROSS_MODULE") only affects which Groq
    model gets used -- ignored for the ollama/anthropic/gemini overrides,
    which are single-model backends by nature. Two different Groq models
    on purpose: qwen/qwen3.8-27b (fast) for the high-volume MONO_MODULE
    case, openai/gpt-oss-120b (stronger reasoning) for CROSS_MODULE, which
    has to correctly model a relationship between several classes instead
    of instantiating just one."""
    if backend == "ollama" or (backend is None and _ollama_reachable()):
        model = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")
        print(f"[commun] Ollama -> client direct HTTP (model='{model}').")
        return OllamaDirectChat(model=model)
    if backend == "anthropic" or (backend is None and os.environ.get("ANTHROPIC_API_KEY")):
        from langchain_anthropic import ChatAnthropic
        print("[commun] ANTHROPIC_API_KEY -> ChatAnthropic.")
        return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    if backend == "gemini" or (
        backend is None
        and (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    ):
        from langchain_google_genai import ChatGoogleGenerativeAI
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        print("[commun] GEMINI_API_KEY -> ChatGoogleGenerativeAI.")
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=key)

    groq_keys = _load_multi_keys("GROQ_API_KEYS", "GROQ_API_KEY")
    if backend == "groq" or (backend is None and groq_keys):
        if not groq_keys:
            raise RuntimeError("--llm-backend groq demande mais aucune GROQ_API_KEYS/GROQ_API_KEY trouvee.")
        if category == "CROSS_MODULE":
            model = os.environ.get("GROQ_MODEL_PHASE2_CROSS", "openai/gpt-oss-120b")
        else:
            model = os.environ.get("GROQ_MODEL_PHASE2_MONO", "qwen/qwen3.8-27b")
        from langchain_groq import ChatGroq
        clients = [ChatGroq(model=model, api_key=k, temperature=0) for k in groq_keys]
        llm = RoundRobinChat(clients, f"Groq({model})") if len(clients) > 1 else clients[0]
        print(f"[commun] GROQ_API_KEYS ({len(groq_keys)} key(s)) -> ChatGroq round-robin, "
              f"model='{model}' (category={category or 'MONO_MODULE'}).")
        return llm

    raise RuntimeError(
        "Aucun backend LLM disponible. Lancez Ollama ou définissez "
        "GROQ_API_KEYS / ANTHROPIC_API_KEY / GEMINI_API_KEY."
    )



@dataclass
class ScenarioProcessingResult:
    scenario_id: str
    agent: str
    category: str
    n_matched_classes: int
    out_path: Optional[Path]
    execution_success: Optional[bool]
    error: Optional[str] = None


def output_path_for(
    category: str, scenario_id: str, scenario_type: str, output_dir: Path
) -> Path:
    category_dir = output_dir / category.lower()
    category_dir.mkdir(parents=True, exist_ok=True)
    func_id = re.sub(r"[^a-z0-9_]", "_", scenario_id.lower())
    return category_dir / f"script_{func_id}_{(scenario_type or 'unknown').lower()}.py"


def resolve_matched_classes(
    entity_names: list[str],
    class_lookup: dict[str, ClassInfo],
    scenario_id: str,
    log_prefix: str = "commun",
) -> list[ClassInfo]:
    matched: list[ClassInfo] = []
    for name in entity_names:
        ci = class_lookup.get(name)
        if ci is None:
            print(f"[{log_prefix}] AVERTISSEMENT: {scenario_id}: '{name}' introuvable -- ignoré.")
            continue
        if ci.is_enum:
            print(f"[{log_prefix}] INFO: {scenario_id}: '{name}' est un Enum -- pas instancié.")
            continue
        matched.append(ci)
    return matched


def load_scenarios(path: str) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))["scenarios"]



@dataclass
class SharedContext:
    class_lookup: dict[str, ClassInfo]
    kb_index: KBIndex
    relation_graph: ModuleRelationGraph
    retriever: Optional[object]
    flync_src_root: Path
    known_modules: set[str]


def build_shared_context(use_rag: bool = True) -> SharedContext:
    print("[commun] Analyse de la KB via l'Agent Lecteur/Analyste ...")
    agent = AgentLecteurAnalyste(FLYNC_KB)
    full_report: KBAnalysisReport = agent.run()

    class_lookup = full_report.build_class_lookup()
    flync_src_root = agent.repo_dir / "src"
    known_modules: set[str] = {ci.module for ci in class_lookup.values() if ci.module}

    kb_index = KBIndex(agent.repo_dir)
    kb_index.build_from_model(agent, full_report)
    kb_index.build_from_sdk()

    relation_graph = build_module_relation_graph(full_report)
    print(
        f"[commun] Graphe : {relation_graph.total_edges} lien(s), "
        f"{len(relation_graph.bridge_class_index)} classe(s)-pont."
    )

    retriever = None
    if use_rag:
        try:
            from phase2.src.flync_pipeline.kb_retriever import HybridKBRetriever
            retriever = HybridKBRetriever()
            retriever.index_classes(list(class_lookup.values()))
            print(f"[commun] RAG actif ({retriever.indexed_class_count} classe(s)).")
        except ImportError as exc:
            print(f"[commun] RAG désactivé ({exc}).")

    return SharedContext(
        class_lookup=class_lookup, kb_index=kb_index,
        relation_graph=relation_graph, retriever=retriever,
        flync_src_root=flync_src_root, known_modules=known_modules,
    )
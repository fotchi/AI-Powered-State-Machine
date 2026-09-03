"""
module_analyzer.py
===================

Agent Lecteur/Analyste du pipeline FLYNC.

Responsable de l'analyse statique AST parallélisée des 12 modules du domaine
FLYNC (app, bus, communication, someip, topology, ecu, metadata, nm, security,
signal, tsn, safety). Pour chaque module Python trouvé sur le disque, ce
composant extrait :

    - les classes définies (dataclasses, classes Pydantic, classes "brutes"),
    - les classes de base (héritage),
    - les champs typés, y compris les types complexes ``Annotated[...]``,
    - les validateurs (fonctions décorées ``@validator``/``@field_validator``),
    - les docstrings de classe et de module,
    - les imports (utilisés ensuite pour construire le graphe de relations).

L'analyse est parallélisée via ``concurrent.futures.ProcessPoolExecutor``
(un processus par module), avec repli automatique sur
``ThreadPoolExecutor`` si le pickling inter-processus échoue (environnements
restreints, notebooks, etc.).
"""

from __future__ import annotations

import ast
import concurrent.futures
import logging
import os
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

logger = logging.getLogger("flync.module_analyzer")

# Les 12 modules FLYNC officiels, dans l'ordre de la spécification.
FLYNC_MODULES: Tuple[str, ...] = (
    "app",
    "bus",
    "communication",
    "someip",
    "topology",
    "ecu",
    "metadata",
    "nm",
    "security",
    "signal",
    "tsn",
    "safety",
)


# --------------------------------------------------------------------------- #
# Structures de données
# --------------------------------------------------------------------------- #

@dataclass
class FieldMetadata:
    """Représente un champ typé d'une classe (attribut annoté)."""

    name: str
    type_repr: str
    is_annotated_complex: bool = False
    default_repr: Optional[str] = None
    constraints: List[str] = field(default_factory=list)


@dataclass
class ValidatorMetadata:
    """Représente un validateur Pydantic (v1 ou v2) attaché à une classe."""

    function_name: str
    decorator_name: str
    targeted_fields: List[str] = field(default_factory=list)
    lineno: int = 0


@dataclass
class ClassMetadata:
    """Représente une classe extraite d'un module FLYNC."""

    module: str
    class_name: str
    qualified_name: str
    bases: List[str] = field(default_factory=list)
    docstring: str = ""
    fields: List[FieldMetadata] = field(default_factory=list)
    validators: List[ValidatorMetadata] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    lineno: int = 0
    file_path: str = ""
    is_dataclass: bool = False
    is_pydantic_model: bool = False


@dataclass
class ModuleAnalysisResult:
    """Résultat d'analyse AST pour un module unique."""

    module: str
    file_path: str
    classes: List[ClassMetadata] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    from_imports: Dict[str, List[str]] = field(default_factory=dict)
    module_docstring: str = ""
    parse_error: Optional[str] = None
    duration_seconds: float = 0.0


@dataclass
class KnowledgeBase:
    """Base de connaissance agrégée sur l'ensemble des modules FLYNC."""

    modules: Dict[str, ModuleAnalysisResult] = field(default_factory=dict)
    class_lookup: Dict[str, ClassMetadata] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)

    def all_classes(self) -> List[ClassMetadata]:
        return list(self.class_lookup.values())

    def classes_in_module(self, module: str) -> List[ClassMetadata]:
        result = self.modules.get(module)
        if result is None:
            return []
        return result.classes


# --------------------------------------------------------------------------- #
# Visiteur AST
# --------------------------------------------------------------------------- #

_PYDANTIC_BASE_HINTS = {"BaseModel", "BaseSettings", "RootModel"}
_VALIDATOR_DECORATOR_NAMES = {
    "validator",
    "field_validator",
    "model_validator",
    "root_validator",
}


def _unparse(node: Optional[ast.AST]) -> str:
    """Convertit un noeud AST en représentation texte, en gérant les erreurs."""
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - filet de sécurité
        return "<unparsable>"


def _extract_decorator_name(dec_node: ast.AST) -> str:
    if isinstance(dec_node, ast.Call):
        dec_node = dec_node.func
    if isinstance(dec_node, ast.Attribute):
        return dec_node.attr
    if isinstance(dec_node, ast.Name):
        return dec_node.id
    return _unparse(dec_node)


def _extract_validator_targets(dec_node: ast.AST) -> List[str]:
    """Extrait les noms de champs ciblés par un décorateur @validator("a", "b")."""
    targets: List[str] = []
    if isinstance(dec_node, ast.Call):
        for arg in dec_node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                targets.append(arg.value)
    return targets


class _ModuleVisitor(ast.NodeVisitor):
    """Parcourt un module et construit la liste des ClassMetadata."""

    def __init__(self, module: str, file_path: str, source_lines: Sequence[str]):
        self.module = module
        self.file_path = file_path
        self.source_lines = source_lines
        self.classes: List[ClassMetadata] = []
        self.imports: List[str] = []
        self.from_imports: Dict[str, List[str]] = {}

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        mod = node.module or ""
        names = [alias.name for alias in node.names]
        self.from_imports.setdefault(mod, []).extend(names)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        bases = [_unparse(b) for b in node.bases]
        is_dataclass = any(
            _extract_decorator_name(dec) == "dataclass" for dec in node.decorator_list
        )
        is_pydantic = any(
            base.split(".")[-1] in _PYDANTIC_BASE_HINTS for base in bases
        )

        docstring = ast.get_docstring(node) or ""
        cls_meta = ClassMetadata(
            module=self.module,
            class_name=node.name,
            qualified_name=f"{self.module}.{node.name}",
            bases=bases,
            docstring=docstring,
            lineno=node.lineno,
            file_path=self.file_path,
            is_dataclass=is_dataclass,
            is_pydantic_model=is_pydantic,
        )

        for stmt in node.body:
            self._process_class_body_stmt(stmt, cls_meta)

        self.classes.append(cls_meta)
        # Ne pas descendre dans les classes imbriquées comme classes de premier
        # niveau du module : on les visite quand même pour capter les
        # validateurs/champs mais sans generic_visit récursif incontrôlé.
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                self.visit_ClassDef(child)

    def _process_class_body_stmt(self, stmt: ast.stmt, cls_meta: ClassMetadata) -> None:
        # Champs annotés : name: Type = default
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            type_repr = _unparse(stmt.annotation)
            is_complex_annotated = type_repr.strip().startswith("Annotated[")
            default_repr = _unparse(stmt.value) if stmt.value is not None else None
            constraints = self._extract_annotated_constraints(stmt.annotation)
            cls_meta.fields.append(
                FieldMetadata(
                    name=stmt.target.id,
                    type_repr=type_repr,
                    is_annotated_complex=is_complex_annotated,
                    default_repr=default_repr,
                    constraints=constraints,
                )
            )
            return

        # Méthodes et validateurs
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cls_meta.methods.append(stmt.name)
            for dec in stmt.decorator_list:
                dec_name = _extract_decorator_name(dec)
                if dec_name in _VALIDATOR_DECORATOR_NAMES:
                    cls_meta.validators.append(
                        ValidatorMetadata(
                            function_name=stmt.name,
                            decorator_name=dec_name,
                            targeted_fields=_extract_validator_targets(dec),
                            lineno=stmt.lineno,
                        )
                    )
            return

    @staticmethod
    def _extract_annotated_constraints(annotation: ast.AST) -> List[str]:
        """Extrait les métadonnées de contrainte d'un ``Annotated[T, ...]``."""
        constraints: List[str] = []
        if (
            isinstance(annotation, ast.Subscript)
            and _unparse(annotation.value).split(".")[-1] == "Annotated"
        ):
            sl = annotation.slice
            elts = sl.elts if isinstance(sl, ast.Tuple) else [sl]
            # Le premier élément est le type réel, le reste sont des métadonnées.
            for extra in elts[1:]:
                constraints.append(_unparse(extra))
        return constraints


# --------------------------------------------------------------------------- #
# Analyse d'un module unique (fonction top-level : nécessaire pour le pickling
# par ProcessPoolExecutor)
# --------------------------------------------------------------------------- #

def _resolve_module_file(module_name: str, search_paths: Sequence[str]) -> Optional[str]:
    """Trouve le fichier source d'un module FLYNC parmi plusieurs racines."""
    candidates = [
        f"{module_name}.py",
        os.path.join(module_name, "__init__.py"),
    ]
    for root in search_paths:
        for candidate in candidates:
            full = os.path.join(root, candidate)
            if os.path.isfile(full):
                return full
    return None


def analyze_single_module(module_name: str, file_path: str) -> ModuleAnalysisResult:
    """
    Analyse AST complète d'un module unique. Fonction pure et picklable,
    utilisée comme unité de travail pour le pool de processus.

    :param module_name: nom logique du module FLYNC (ex: "someip").
    :param file_path: chemin du fichier source Python à analyser.
    :return: ModuleAnalysisResult contenant classes, imports et erreurs.
    """
    start = time.perf_counter()
    result = ModuleAnalysisResult(module=module_name, file_path=file_path)

    if not file_path or not os.path.isfile(file_path):
        result.parse_error = f"Fichier introuvable pour le module '{module_name}': {file_path}"
        result.duration_seconds = time.perf_counter() - start
        return result

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            source = fh.read()
    except OSError as exc:
        result.parse_error = f"Erreur de lecture du fichier '{file_path}': {exc}"
        result.duration_seconds = time.perf_counter() - start
        return result

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as exc:
        result.parse_error = f"Erreur de syntaxe dans '{file_path}': {exc}"
        result.duration_seconds = time.perf_counter() - start
        return result

    try:
        result.module_docstring = ast.get_docstring(tree) or ""
        visitor = _ModuleVisitor(module_name, file_path, source.splitlines())
        visitor.visit(tree)
        result.classes = visitor.classes
        result.imports = visitor.imports
        result.from_imports = visitor.from_imports
    except Exception as exc:  # pragma: no cover - filet de sécurité
        result.parse_error = (
            f"Erreur inattendue lors de l'analyse AST de '{file_path}': {exc}\n"
            f"{traceback.format_exc()}"
        )

    result.duration_seconds = time.perf_counter() - start
    return result


# --------------------------------------------------------------------------- #
# Orchestration parallèle
# --------------------------------------------------------------------------- #

class ParallelModuleAnalyzer:
    """
    Analyse en parallèle les 12 modules FLYNC via ``ProcessPoolExecutor``.

    En cas d'échec du pool de processus (environnement sans fork disponible,
    restrictions de sandboxing, erreur de pickling), l'analyseur bascule
    automatiquement sur un ``ThreadPoolExecutor`` afin de garantir la
    complétion du pipeline.
    """

    def __init__(
        self,
        search_paths: Optional[Sequence[str]] = None,
        modules: Sequence[str] = FLYNC_MODULES,
        max_workers: Optional[int] = None,
    ) -> None:
        self.search_paths: List[str] = list(search_paths) if search_paths else ["."]
        self.modules: Tuple[str, ...] = tuple(modules)
        self.max_workers = max_workers or min(len(self.modules), (os.cpu_count() or 4))

    def _resolve_all_paths(self) -> Dict[str, Optional[str]]:
        return {
            module: _resolve_module_file(module, self.search_paths)
            for module in self.modules
        }

    def analyze(self) -> KnowledgeBase:
        """
        Lance l'analyse AST parallèle de tous les modules configurés et
        agrège les résultats dans une :class:`KnowledgeBase`.
        """
        file_paths = self._resolve_all_paths()
        kb = KnowledgeBase()

        try:
            results = self._run_with_executor(
                concurrent.futures.ProcessPoolExecutor, file_paths
            )
        except (OSError, PermissionError, RuntimeError) as exc:
            logger.warning(
                "ProcessPoolExecutor indisponible (%s), repli sur ThreadPoolExecutor.",
                exc,
            )
            results = self._run_with_executor(
                concurrent.futures.ThreadPoolExecutor, file_paths
            )

        for module_name, module_result in results.items():
            kb.modules[module_name] = module_result
            if module_result.parse_error:
                kb.errors[module_name] = module_result.parse_error
                logger.error("Module '%s': %s", module_name, module_result.parse_error)
                continue
            for cls in module_result.classes:
                kb.class_lookup[cls.qualified_name] = cls
                # Alias court additionnel : NomDeClasse -> premier match gagne,
                # sauf collision explicite (loggée).
                if cls.class_name not in kb.class_lookup:
                    kb.class_lookup[cls.class_name] = cls
                elif kb.class_lookup[cls.class_name].module != module_name:
                    logger.debug(
                        "Collision de nom de classe '%s' entre modules '%s' et '%s'.",
                        cls.class_name,
                        kb.class_lookup[cls.class_name].module,
                        module_name,
                    )

        return kb

    def _run_with_executor(
        self,
        executor_cls,
        file_paths: Dict[str, Optional[str]],
    ) -> Dict[str, ModuleAnalysisResult]:
        results: Dict[str, ModuleAnalysisResult] = {}
        with executor_cls(max_workers=self.max_workers) as executor:
            future_to_module = {
                executor.submit(analyze_single_module, module, path): module
                for module, path in file_paths.items()
            }
            for future in concurrent.futures.as_completed(future_to_module):
                module_name = future_to_module[future]
                try:
                    results[module_name] = future.result()
                except Exception as exc:  # pragma: no cover - filet de sécurité
                    logger.error(
                        "Échec critique de l'analyse du module '%s': %s",
                        module_name,
                        exc,
                    )
                    results[module_name] = ModuleAnalysisResult(
                        module=module_name,
                        file_path=file_paths.get(module_name) or "",
                        parse_error=str(exc),
                    )
        return results


# --------------------------------------------------------------------------- #
# Graphe de dépendances entre modules
# --------------------------------------------------------------------------- #

class ModuleRelationGraph:
    """
    Graphe orienté des dépendances entre les 12 modules FLYNC, construit à
    partir des imports détectés et des relations d'héritage entre classes.

    Implémentation sans dépendance externe (pas de ``networkx`` requis) :
    structure de liste d'adjacence maison, suffisante pour l'usage du
    pipeline (requêtes de voisinage, détection de cycles, tri topologique).
    """

    def __init__(self) -> None:
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Set[str]] = {}
        self.edge_reasons: Dict[Tuple[str, str], Set[str]] = {}

    def add_node(self, module: str) -> None:
        self.nodes.add(module)
        self.edges.setdefault(module, set())

    def add_edge(self, source: str, target: str, reason: str) -> None:
        if source == target:
            return
        self.add_node(source)
        self.add_node(target)
        self.edges[source].add(target)
        self.edge_reasons.setdefault((source, target), set()).add(reason)

    def successors(self, module: str) -> Set[str]:
        return self.edges.get(module, set())

    def predecessors(self, module: str) -> Set[str]:
        return {src for src, targets in self.edges.items() if module in targets}

    def has_cycle(self) -> bool:
        visited: Set[str] = set()
        stack: Set[str] = set()

        def _dfs(node: str) -> bool:
            visited.add(node)
            stack.add(node)
            for neighbor in self.edges.get(node, set()):
                if neighbor not in visited:
                    if _dfs(neighbor):
                        return True
                elif neighbor in stack:
                    return True
            stack.discard(node)
            return False

        return any(_dfs(node) for node in self.nodes if node not in visited)

    def topological_order(self) -> List[str]:
        """Tri topologique (Kahn). Les cycles restants sont ajoutés en fin de liste."""
        in_degree = {node: 0 for node in self.nodes}
        for targets in self.edges.values():
            for t in targets:
                in_degree[t] = in_degree.get(t, 0) + 1

        queue = [n for n, d in in_degree.items() if d == 0]
        order: List[str] = []
        queue.sort()
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in sorted(self.edges.get(node, set())):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
            queue.sort()

        remaining = [n for n in self.nodes if n not in order]
        order.extend(sorted(remaining))
        return order

    def to_dict(self) -> Dict[str, List[str]]:
        return {node: sorted(targets) for node, targets in self.edges.items()}


def build_module_relation_graph(kb: KnowledgeBase) -> ModuleRelationGraph:
    """
    Construit le ``ModuleRelationGraph`` à partir des données AST agrégées
    dans la KnowledgeBase : une arête module_a -> module_b est ajoutée si
    module_a importe module_b, ou si une classe de module_a hérite d'une
    classe définie dans module_b.
    """
    graph = ModuleRelationGraph()
    module_names = set(kb.modules.keys())

    for module_name, module_result in kb.modules.items():
        graph.add_node(module_name)
        if module_result.parse_error:
            continue

        # Relations d'import direct.
        for imported in module_result.imports:
            root = imported.split(".")[0]
            if root in module_names:
                graph.add_edge(module_name, root, reason="import")

        for from_module in module_result.from_imports:
            root = (from_module or "").split(".")[0]
            if root in module_names:
                graph.add_edge(module_name, root, reason="from_import")

        # Relations d'héritage : si une base référencée existe dans un
        # autre module connu, on ajoute une arête de dépendance.
        for cls in module_result.classes:
            for base in cls.bases:
                base_simple = base.split(".")[-1]
                owner = kb.class_lookup.get(base_simple)
                if owner is not None and owner.module != module_name:
                    graph.add_edge(module_name, owner.module, reason=f"inherit:{cls.class_name}->{base_simple}")

    return graph


# --------------------------------------------------------------------------- #
# Point d'entrée utilitaire (exécution directe / debug)
# --------------------------------------------------------------------------- #

def analyze_flync_knowledge_base(
    search_paths: Optional[Sequence[str]] = None,
    modules: Sequence[str] = FLYNC_MODULES,
    max_workers: Optional[int] = None,
) -> Tuple[KnowledgeBase, ModuleRelationGraph]:
    """
    Fonction utilitaire de haut niveau : lance l'analyse parallèle des
    modules FLYNC puis construit le graphe de dépendances associé.
    """
    analyzer = ParallelModuleAnalyzer(
        search_paths=search_paths, modules=modules, max_workers=max_workers
    )
    kb = analyzer.analyze()
    graph = build_module_relation_graph(kb)
    return kb, graph


if __name__ == "__main__":  # pragma: no cover - usage manuel
    logging.basicConfig(level=logging.INFO)
    kb_result, relation_graph = analyze_flync_knowledge_base(search_paths=[str(Path.cwd())])
    logger.info("Modules analysés : %d", len(kb_result.modules))
    logger.info("Classes indexées : %d", len(kb_result.all_classes()))
    logger.info("Ordre topologique des modules : %s", relation_graph.topological_order())
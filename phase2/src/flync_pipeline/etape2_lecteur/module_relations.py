

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from .agent_lecteur_analyste import KBAnalysisReport


class ModuleRelationGraph:
  

    def __init__(self) -> None:
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Set[str]] = {}
        self.edge_reasons: Dict[Tuple[str, str], Set[str]] = {}
        self.bridge_class_index: Dict[str, Set[str]] = {}

    @property
    def total_edges(self) -> int:
        """Nombre total d'arêtes (source, target) distinctes du graphe."""
        return sum(len(targets) for targets in self.edges.values())

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


def _resolve_cross_import_module(imported_dotted_path: str, known_modules: Set[str]) -> str | None:
  
    segments = imported_dotted_path.split(".")
    for segment in segments:
        if segment in known_modules:
            return segment
    return None


def build_module_relation_graph(report: KBAnalysisReport) -> ModuleRelationGraph:
   
    graph = ModuleRelationGraph()
    known_modules = set(report.modules.keys())
    class_lookup = report.build_class_lookup()

    for module_name, module_analysis in report.modules.items():
        graph.add_node(module_name)

        for imported_path, imported_names in module_analysis.cross_module_imports.items():
            target_module = _resolve_cross_import_module(imported_path, known_modules)
            if target_module is not None:
                graph.add_edge(module_name, target_module, reason=f"import:{imported_path}")
                for cls_name in imported_names:
                    graph.bridge_class_index.setdefault(cls_name, set()).update(
                        {module_name, target_module}
                    )

        # Arêtes issues de l'héritage inter-module.
        for cls in module_analysis.classes.values():
            for base in cls.bases:
                owner = class_lookup.get(base)
                if owner is not None and owner.module != module_name:
                    graph.add_edge(
                        module_name, owner.module, reason=f"inherit:{cls.name}->{base}"
                    )
                    graph.bridge_class_index.setdefault(base, set()).update(
                        {module_name, owner.module}
                    )

    return graph
"""
Graph Analyzer — Etape 2.

Reads every downloaded .py file with `ast` (no execution), builds:
  1. A class index: which domain defines which Pydantic class
  2. A field index: for every class, its fields and their type annotations
  3. A cross-domain relation graph (nx.DiGraph): domain A -> domain B
     whenever a class in A has a field typed with a class defined in B,
     with real field/class names kept as edge evidence for the LLM step.
"""
import ast
import json
import os
import networkx as nx

SOURCE_DIR = "data/flync_source"
GRAPH_OUTPUT_DIR = "data/flync_graph"
CLASS_INDEX_FILE = f"{GRAPH_OUTPUT_DIR}/class_index.json"
RELATIONS_FILE = f"{GRAPH_OUTPUT_DIR}/relations.json"


class ClassInfo:
    __slots__ = ("name", "domain", "file", "bases", "fields")

    def __init__(self, name: str, domain: str, file: str, bases: list[str]):
        self.name = name
        self.domain = domain
        self.file = file
        self.bases = bases
        self.fields: list[tuple[str, list[str]]] = []  # (field_name, referenced_type_names)


def _extract_type_names(annotation_node: ast.expr) -> list[str]:
    """Given a field's type annotation AST node (e.g. list[ECUPort],
    Optional[Controller], Frame), returns every identifier name used in
    it -- e.g. ["list", "ECUPort"] or ["Optional", "Controller"].
    We only care about the actual class names (filtered later against
    the class index), so grabbing everything here is fine.
    """
    names = []
    for node in ast.walk(annotation_node):
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            # Handles forward references written as strings: "ECUPort"
            names.append(node.value)
    return names


def parse_file(filepath: str, domain: str) -> list[ClassInfo]:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        print(f"  [!] Syntax error in {filepath}: {e}")
        return []

    classes = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
        info = ClassInfo(name=node.name, domain=domain, file=filepath, bases=bases)

        for item in node.body:
            # A Pydantic field looks like: field_name: SomeType [= default]
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_name = item.target.id
                referenced = _extract_type_names(item.annotation)
                info.fields.append((field_name, referenced))

        classes.append(info)
    return classes


def build_class_index() -> dict[str, ClassInfo]:
    """First pass: which domain defines each class name."""
    index: dict[str, ClassInfo] = {}
    for domain in sorted(os.listdir(SOURCE_DIR)):
        domain_path = os.path.join(SOURCE_DIR, domain)
        if not os.path.isdir(domain_path):
            continue
        for fname in os.listdir(domain_path):
            if not fname.endswith(".py"):
                continue
            filepath = os.path.join(domain_path, fname)
            for cls in parse_file(filepath, domain):
                index[cls.name] = cls
    return index


def build_relation_graph(class_index: dict[str, ClassInfo]) -> nx.DiGraph:
    """Second pass: for every field in every class, if its type
    references a class from a DIFFERENT domain, add a directed edge
    domain -> domain, incrementing weight and recording evidence.
    """
    graph = nx.DiGraph()
    for domain_name in sorted({c.domain for c in class_index.values()}):
        graph.add_node(domain_name)

    for cls in class_index.values():
        for field_name, referenced_names in cls.fields:
            for ref_name in referenced_names:
                target_cls = class_index.get(ref_name)
                if target_cls is None or target_cls.domain == cls.domain:
                    continue  # not a known class, or same-domain (not cross-module)

                src, dst = cls.domain, target_cls.domain
                if graph.has_edge(src, dst):
                    graph[src][dst]["weight"] += 1
                    graph[src][dst]["evidence"].append(
                        f"{cls.name}.{field_name} -> {target_cls.name}"
                    )
                else:
                    graph.add_edge(src, dst, weight=1, evidence=[
                        f"{cls.name}.{field_name} -> {target_cls.name}"
                    ])
    return graph


def save_class_index(class_index: dict[str, ClassInfo]) -> None:
    os.makedirs(GRAPH_OUTPUT_DIR, exist_ok=True)
    serializable = {
        name: {
            "domain": cls.domain,
            "file": cls.file,
            "bases": cls.bases,
            "fields": [[fname, refs] for fname, refs in cls.fields],
        }
        for name, cls in class_index.items()
    }
    with open(CLASS_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)


def save_relation_graph(graph: nx.DiGraph) -> None:
    os.makedirs(GRAPH_OUTPUT_DIR, exist_ok=True)
    payload = {
        "nodes": list(graph.nodes()),
        "edges": [
            {"source": src, "target": dst, "weight": data["weight"], "evidence": data["evidence"]}
            for src, dst, data in graph.edges(data=True)
        ],
    }
    with open(RELATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def load_relation_graph() -> nx.DiGraph:
    """Used by the LLM Orchestrator (step 3) -- rebuilds the DiGraph from
    the saved JSON instead of re-parsing all source files every time."""
    with open(RELATIONS_FILE, encoding="utf-8") as f:
        payload = json.load(f)
    graph = nx.DiGraph()
    graph.add_nodes_from(payload["nodes"])
    for edge in payload["edges"]:
        graph.add_edge(edge["source"], edge["target"], weight=edge["weight"], evidence=edge["evidence"])
    return graph


if __name__ == "__main__":
    print("Building class index...")
    class_index = build_class_index()
    print(f"Found {len(class_index)} classes across all domains\n")

    print("Building cross-domain relation graph...")
    graph = build_relation_graph(class_index)
    print(f"Graph: {graph.number_of_nodes()} nodes (domains), {graph.number_of_edges()} edges (relations)\n")

    save_class_index(class_index)
    save_relation_graph(graph)
    print(f"Saved: {CLASS_INDEX_FILE}")
    print(f"Saved: {RELATIONS_FILE}\n")

    print("--- Edges sorted by weight (strongest relations first) ---")
    edges_sorted = sorted(graph.edges(data=True), key=lambda e: -e[2]["weight"])
    for src, dst, data in edges_sorted[:15]:
        print(f"  {src} -> {dst}  (weight={data['weight']})")
        for ev in data["evidence"][:2]:
            print(f"      e.g. {ev}")
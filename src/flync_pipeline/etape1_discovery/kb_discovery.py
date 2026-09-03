from __future__ import annotations
 
import ast
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
 
from src.flync_pipeline.etape1_discovery.kb_pointers import FLYNC_KB, KBPointers
 
REPO_CACHE_DIR = Path("./_flync_kb_cache")
 
 
def sync_repo(pointers: KBPointers, repo_dir: Path = REPO_CACHE_DIR) -> Path:
    if not (repo_dir / ".git").exists():
        print(f"[kb] Clonage de {pointers.repo_url} (branche {pointers.branch}) ...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", pointers.branch, pointers.repo_url, str(repo_dir)],
            check=True,
        )
    else:
        print(f"[kb] Depot deja present -> pull --ff-only pour refleter l'etat actuel du repo ...")
        subprocess.run(["git", "-C", str(repo_dir), "pull", "--ff-only"], check=False)
    return repo_dir
 
 
def discover_modules(repo_dir: Path, pointers: KBPointers) -> list[str]:
    """Liste les sous-dossiers de `model_root_path` qui sont de vrais modules
    Python (presence d'un __init__.py), au moment de l'execution."""
    model_root = repo_dir / pointers.model_root_path
    if not model_root.is_dir():
        raise FileNotFoundError(f"Racine KB introuvable: {model_root}")
 
    modules = []
    for entry in sorted(model_root.iterdir()):
        if entry.is_dir() and (entry / "__init__.py").exists():
            modules.append(entry.name)
    return modules
 

@dataclass
class ModuleMap:
    name: str
    file_count: int
    class_count: int
    public_api: list[str] = field(default_factory=list)
    depends_on: set[str] = field(default_factory=set)  # autres modules flync_4_* importes
 
 
def _extract_module_name_from_import(import_from: str) -> str | None:
    """'flync.model.flync_4_someip.deployments' -> 'flync_4_someip'"""
    parts = import_from.split(".")
    for p in parts:
        if p.startswith("flync_4_"):
            return p
    return None
 
 
def map_module(repo_dir: Path, module_name: str) -> ModuleMap:
    module_dir = repo_dir / FLYNC_KB.model_root_path / module_name
    py_files = list(module_dir.glob("*.py"))
 
    class_count = 0
    public_api: list[str] = []
    depends_on: set[str] = set()
 
    for f in py_files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
 
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_count += 1
 
            if isinstance(node, ast.ImportFrom) and node.module and "flync.model.flync_4_" in node.module:
                other = _extract_module_name_from_import(node.module)
                if other and other != module_name:
                    depends_on.add(other)
 
            if f.name == "__init__.py" and isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "__all__"
                        and isinstance(node.value, (ast.List, ast.Tuple))
                    ):
                        public_api = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
 
    return ModuleMap(
        name=module_name,
        file_count=len(py_files),
        class_count=class_count,
        public_api=public_api,
        depends_on=depends_on,
    )
 
 
def build_kb_cartography(pointers: KBPointers = FLYNC_KB) -> dict[str, ModuleMap]:
    repo_dir = sync_repo(pointers)
    modules = discover_modules(repo_dir, pointers)
    print(f"[kb] {len(modules)} module(s) decouvert(s) dynamiquement: {modules}")
 
    cartography: dict[str, ModuleMap] = {}
    for m in modules:
        cartography[m] = map_module(repo_dir, m)
 
    return cartography
 

def resolve_dependency_closure(cartography: dict[str, ModuleMap], target_modules: list[str]) -> set[str]:
    """Etant donne une liste de modules cibles (le perimetre d'un scenario
    KPIT), retourne la fermeture transitive des modules necessaires (le
    module lui-meme + tout ce dont il depend, recursivement)."""
    closure: set[str] = set()
    stack = list(target_modules)
 
    while stack:
        m = stack.pop()
        if m in closure:
            continue
        if m not in cartography:
            raise KeyError(f"Module '{m}' inconnu de la KB (modules disponibles: {sorted(cartography)})")
        closure.add(m)
        stack.extend(cartography[m].depends_on)
 
    return closure
 
 
if __name__ == "__main__":
    cartography = build_kb_cartography()
 
    print("\n=== Cartographie KB (decouverte dynamique) ===")
    for name, m in sorted(cartography.items()):
        deps = ", ".join(sorted(m.depends_on)) if m.depends_on else "-"
        print(f"  {name:28s} | {m.file_count:2d} fichiers | {m.class_count:3d} classes | depend de: {deps}")
 
    print("\n=== Test de resolution multi-module (exemple ECU) ===")
    closure = resolve_dependency_closure(cartography, ["flync_4_ecu"])
    print(f"  flync_4_ecu necessite (fermeture transitive): {sorted(closure)}")
 
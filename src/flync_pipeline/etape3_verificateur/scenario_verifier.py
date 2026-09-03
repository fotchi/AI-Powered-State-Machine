from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..etape2_lecteur.agent_lecteur_analyste import AgentLecteurAnalyste
from ..etape1_discovery.kb_pointers import FLYNC_KB
from ..etape2_lecteur.module_relations import ModuleRelationGraph, build_module_relation_graph

SDK_SUBPATHS = ["sdk/workspace", "sdk/utils"]


@dataclass
class EntityLocation:
    name: str
    layer: str
    location: str


class KBIndex:

    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.entities: dict[str, EntityLocation] = {}

    def build_from_model(self, agent: AgentLecteurAnalyste, report) -> None:
        for module_name, analysis in report.modules.items():
            for class_name in analysis.classes:
                self.entities.setdefault(
                    class_name, EntityLocation(class_name, "model", module_name)
                )

    def build_from_sdk(self) -> None:
        for subpath in SDK_SUBPATHS:
            sdk_dir = self.repo_dir / "src" / "flync" / subpath
            if not sdk_dir.is_dir():
                continue
            for py_file in sorted(sdk_dir.glob("*.py")):
                try:
                    tree = ast.parse(py_file.read_text(encoding="utf-8"))
                except SyntaxError:
                    continue
                rel = str(py_file.relative_to(self.repo_dir))
                for node in tree.body:
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        self.entities.setdefault(node.name, EntityLocation(node.name, "sdk", rel))

    def find_mentions(self, text: str) -> list[EntityLocation]:
        found = []
        for name, loc in self.entities.items():
            if len(name) < 4:
                continue
            if re.search(rf"\b{re.escape(name)}\b", text):
                found.append(loc)
        return found


def resolve_submodel_field(submodel: str) -> list[str]:
    if submodel.startswith("cross_module"):
        inner = re.search(r"\((.*?)\)", submodel)
        if inner:
            return [m.strip() for m in inner.group(1).split("+")]
        return []
    return [submodel.strip()]


@dataclass
class ScenarioVerdict:
    scenario_id: str
    submodels_declared: list[str]
    entities_found_in_model: list[str] = field(default_factory=list)
    entities_found_in_sdk: list[str] = field(default_factory=list)
    entities_unresolved_hint: list[str] = field(default_factory=list)
    validators_on_matched_classes: dict[str, list[str]] = field(default_factory=dict)
    classification: str = "UNRESOLVED"
    submodels_actually_linked: Optional[bool] = None
    resolved_via_rag: list[str] = field(default_factory=list)


def _check_submodels_actually_linked(
    submodels: list[str],
    relation_graph: Optional[ModuleRelationGraph],
) -> Optional[bool]:
    if relation_graph is None or len(submodels) < 2:
        return None
    for i in range(len(submodels)):
        for j in range(i + 1, len(submodels)):
            a, b = submodels[i], submodels[j]
            if b in relation_graph.successors(a) or a in relation_graph.successors(b):
                return True
    return False


RAG_FALLBACK_MIN_SCORE = 0.25
RAG_FALLBACK_TOP_K = 2


def _resolve_via_rag_fallback(text: str, retriever: object) -> list[str]:
    if retriever is None:
        return []
    try:
        if not retriever.is_ready():
            return []
        result = retriever.retrieve_relevant_classes(
            text, top_k=RAG_FALLBACK_TOP_K, min_score=RAG_FALLBACK_MIN_SCORE
        )
    except Exception as exc:  # pragma: no cover - défense en profondeur
        print(f"[verifier] AVERTISSEMENT: échec du repli RAG ({exc}), ignoré.")
        return []
    return [c.class_metadata.name for c in result.candidates]


def verify_scenario(
    scenario: dict,
    index: KBIndex,
    class_lookup: dict,
    relation_graph: Optional[ModuleRelationGraph] = None,
    retriever: Optional[object] = None,
) -> ScenarioVerdict:
    submodels = resolve_submodel_field(scenario["submodel"])
    text = " ".join([
        scenario.get("title", ""),
        scenario.get("description", ""),
        scenario.get("expected_result", "") or "",
        scenario.get("injected_fault", "") or "",
    ])

    mentions = index.find_mentions(text)
    model_hits = sorted({m.name for m in mentions if m.layer == "model"})
    sdk_hits = sorted({m.name for m in mentions if m.layer == "sdk"})

    resolved_via_rag: list[str] = []
    if not model_hits and not sdk_hits:
        resolved_via_rag = _resolve_via_rag_fallback(text, retriever)
        if resolved_via_rag:
            print(f"[verifier] {scenario['id']}: aucune entité par matching exact, "
                  f"résolu par repli RAG -> {resolved_via_rag}")
        model_hits = sorted(resolved_via_rag)

    if sdk_hits:
        classification = "REQUIRES_SDK"
    elif model_hits:
        classification = "MODEL_ONLY"
    else:
        classification = "UNRESOLVED"

    validators_map: dict[str, list[str]] = {}
    for class_name in model_hits:
        info = class_lookup.get(class_name)
        if info is not None:
            validators_map[class_name] = [v.method_name for v in info.validators] or ["(aucun validator)"]

    return ScenarioVerdict(
        scenario_id=scenario["id"],
        submodels_declared=submodels,
        entities_found_in_model=model_hits,
        entities_found_in_sdk=sdk_hits,
        validators_on_matched_classes=validators_map,
        classification=classification,
        submodels_actually_linked=_check_submodels_actually_linked(submodels, relation_graph),
        resolved_via_rag=resolved_via_rag,
    )


def render_markdown_report(verdicts: list[ScenarioVerdict], scenarios_by_id: dict[str, dict]) -> str:
    lines = [
        "# Vérification automatique des scénarios KPIT",
        "",
        "Générée par `scenario_verifier.py` — indexation réelle de "
        "`src/flync/model` (12 modules) + `src/flync/sdk/{workspace,utils}` "
        "(classes/fonctions de haut niveau uniquement), puis correspondance "
        "de nom contre le texte de chaque scénario.",
        "",
        "| ID | Submodel(s) déclaré(s) | Classification | Entités (model) | Entités (sdk) | Couplage réel |",
        "|---|---|---|---|---|---|",
    ]
    counts = {"MODEL_ONLY": 0, "REQUIRES_SDK": 0, "UNRESOLVED": 0}
    for v in verdicts:
        counts[v.classification] += 1
        model_str = ", ".join(f"`{e}`" for e in v.entities_found_in_model) or "—"
        sdk_str = ", ".join(f"`{e}`" for e in v.entities_found_in_sdk) or "—"
        badge = {"MODEL_ONLY": "✅", "REQUIRES_SDK": "⚠️", "UNRESOLVED": "❓"}[v.classification]
        link_str = (
            "—" if v.submodels_actually_linked is None
            else ("✅ oui" if v.submodels_actually_linked else "⚠️ non")
        )
        lines.append(
            f"| `{v.scenario_id}` | {', '.join(v.submodels_declared)} | {badge} {v.classification} "
            f"| {model_str} | {sdk_str} | {link_str} |"
        )

    lines += [
        "",
        f"**Résumé : {counts['MODEL_ONLY']} model-only, {counts['REQUIRES_SDK']} requièrent le SDK, "
        f"{counts['UNRESOLVED']} non résolus.**",
        "",
        "## Validators réels des classes trouvées, par scénario",
        "",
        "⚠️ Une classe trouvée ne veut pas dire que LA règle métier décrite existe — "
        "seulement que la classe existe. Compare la liste de validators ci-dessous "
        "au `expected_result` du scénario pour juger si la règle a une chance d'y être.",
        "",
    ]
    for v in verdicts:
        if not v.validators_on_matched_classes:
            continue
        lines.append(f"**`{v.scenario_id}`** — *{scenarios_by_id[v.scenario_id]['expected_result']}*")
        for class_name, validators in v.validators_on_matched_classes.items():
            lines.append(f"- `{class_name}` → {', '.join(validators)}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Vérifie des scénarios KPIT contre le vrai code FLYNC.")
    parser.add_argument("--scenarios", required=True, help="Chemin du fichier JSON de scénarios KPIT.")
    parser.add_argument("--output-dir", default="./scenario_verification_out")
    args = parser.parse_args()

    agent = AgentLecteurAnalyste(FLYNC_KB)
    print("[verifier] Analyse complète de la KB (model)...")
    model_report = agent.run()

    print("[verifier] Construction de l'index (model + sdk)...")
    index = KBIndex(agent.repo_dir)
    index.build_from_model(agent, model_report)
    index.build_from_sdk()
    print(f"[verifier]   -> {len(index.entities)} entité(s) indexée(s) au total")

    print("[verifier] Construction du graphe de relations inter-modules...")
    relation_graph = build_module_relation_graph(model_report)
    print(f"[verifier]   -> {relation_graph.total_edges} lien(s), "
          f"{len(relation_graph.bridge_class_index)} classe(s)-pont.")

    class_lookup: dict = model_report.build_class_lookup()

    retriever = None
    try:
        from ..kb_retriever import HybridKBRetriever

        retriever = HybridKBRetriever()
        retriever.index_classes(list(class_lookup.values()))
        print(f"[verifier] Repli RAG actif ({retriever.indexed_class_count} classe(s) indexée(s)).")
    except ImportError as exc:
        print(f"[verifier] Repli RAG désactivé (dépendance manquante: {exc}). "
              f"La résolution reste limitée au matching de nom exact.")

    scenarios_data = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
    scenarios = scenarios_data["scenarios"]
    scenarios_by_id = {s["id"]: s for s in scenarios}
    print(f"[verifier] {len(scenarios)} scénario(s) à vérifier.")

    verdicts = [verify_scenario(s, index, class_lookup, relation_graph, retriever) for s in scenarios]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    (output_dir / "verdicts.json").write_text(
        json.dumps([v.__dict__ for v in verdicts], indent=2), encoding="utf-8"
    )
    (output_dir / "RAPPORT.md").write_text(
        render_markdown_report(verdicts, scenarios_by_id), encoding="utf-8"
    )

    print(f"\n[verifier] Terminé. Rapports -> {output_dir}")
    for v in verdicts:
        print(f"  {v.scenario_id}: {v.classification}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
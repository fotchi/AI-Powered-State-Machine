"""
agent_maitre.py
=================

Orchestrateur Principal (Agent Maître) du pipeline FLYNC.

Exécute la séquence macro complète décrite dans la spécification :

    1. Analyse KB Parallèle (module_analyzer.ParallelModuleAnalyzer)
    2. Graphe de Dépendances (module_analyzer.build_module_relation_graph)
    3. Indexation & Retrieval (kb_retriever.HybridKBRetriever)
    4. Vérification de Scénario (scenario_verifier.ScenarioVerifier)
    5. Mode Dispatching (heuristique template vs llm) puis exécution de la
       boucle micro LangGraph (orchestrateur_langgraph.ScenarioLangGraphOrchestrator)
       pour les scénarios en mode "llm", ou génération directe par gabarit
       pour les scénarios en mode "template".

Produit en sortie un rapport structuré (``PipelineReport``) résumant, pour
chaque scénario : la classe résolue, le niveau de confiance, le mode choisi,
le statut final (SUCCESS/FAILURE) et le code généré.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import textwrap
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence

from flync_pipeline.kb_retriever import HybridKBRetriever
from flync_pipeline.etape2_lecteur.agent_lecteur_analyste import (
    AgentLecteurAnalyste,
    ClassInfo,
    KBAnalysisReport,
)
from flync_pipeline.etape2_lecteur.module_relations import ModuleRelationGraph, build_module_relation_graph
from flync_pipeline.orchestrateur_langgraph import (
    AnthropicDeveloperClient,
    ScenarioLangGraphOrchestrator,
)
from flync_pipeline.etape3_verificateur.scenario_verifier import ConfidenceLevel, ResolutionResult, ScenarioVerifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("flync.agent_maitre")


class DispatchMode(str, Enum):
    """Mode de génération choisi pour un scénario donné."""

    TEMPLATE = "template"
    LLM = "llm"


@dataclass
class ScenarioOutcome:
    """Résultat final du traitement d'un scénario par le pipeline."""

    scenario_id: str
    scenario_text: str
    resolved_class_name: Optional[str]
    resolved_module: Optional[str]
    confidence: str
    dispatch_mode: str
    status: str
    generated_code: str = ""
    retry_count: int = 0
    duration_seconds: float = 0.0
    notes: List[str] = field(default_factory=list)


@dataclass
class PipelineReport:
    """Rapport global d'exécution du pipeline FLYNC."""

    total_modules_analyzed: int
    total_classes_indexed: int
    module_analysis_errors: Dict[str, str]
    topological_module_order: List[str]
    outcomes: List[ScenarioOutcome]
    total_duration_seconds: float

    def to_dict(self) -> dict:
        return {
            "total_modules_analyzed": self.total_modules_analyzed,
            "total_classes_indexed": self.total_classes_indexed,
            "module_analysis_errors": self.module_analysis_errors,
            "topological_module_order": self.topological_module_order,
            "outcomes": [asdict(o) for o in self.outcomes],
            "total_duration_seconds": self.total_duration_seconds,
        }

    def summary(self) -> str:
        success = sum(1 for o in self.outcomes if o.status == "SUCCESS")
        failure = sum(1 for o in self.outcomes if o.status == "FAILURE")
        unresolved = sum(1 for o in self.outcomes if o.confidence == ConfidenceLevel.UNRESOLVED.value)
        lines = [
            "=== Rapport du pipeline FLYNC ===",
            f"Modules analysés      : {self.total_modules_analyzed}",
            f"Classes indexées       : {self.total_classes_indexed}",
            f"Scénarios traités       : {len(self.outcomes)}",
            f"  - SUCCESS            : {success}",
            f"  - FAILURE            : {failure}",
            f"  - Non résolus (KB)   : {unresolved}",
            f"Durée totale            : {self.total_duration_seconds:.2f}s",
        ]
        return "\n".join(lines)


class ModeDispatchHeuristic:
    """
    Heuristique de sélection du mode de génération (``template`` vs
    ``llm``) en fonction du niveau de confiance de résolution du scénario
    et de la disponibilité d'un gabarit connu pour la classe résolue.

    Règles :
        - EXACT ou ALIAS + un gabarit existe pour la classe -> TEMPLATE
          (la classe cible est connue avec certitude et un patron de code
          générique et fiable est disponible : pas besoin d'appeler un LLM).
        - EXACT ou ALIAS sans gabarit disponible -> LLM
          (la classe est connue avec certitude mais nécessite une
          génération sur mesure).
        - RAG_HIGH -> LLM (confiance suffisante pour tenter une génération,
          mais la classe étant issue d'un retrieval sémantique, un template
          rigide serait risqué).
        - RAG_LOW ou UNRESOLVED -> LLM en mode "prudent" (le scénario est
          quand même soumis au LLM avec le meilleur candidat disponible,
          le pipeline le marque explicitement comme faible confiance).
    """

    def __init__(self, known_templates: Optional[Dict[str, str]] = None) -> None:
        self.known_templates = known_templates or {}

    def decide(self, resolution: ResolutionResult) -> DispatchMode:
        class_name = resolution.resolved_class.name if resolution.resolved_class else None

        if resolution.confidence in (ConfidenceLevel.EXACT, ConfidenceLevel.ALIAS):
            if class_name and class_name in self.known_templates:
                return DispatchMode.TEMPLATE
            return DispatchMode.LLM

        return DispatchMode.LLM

    def render_template(self, class_name: str, scenario_text: str) -> str:
        """Rend le gabarit de code associé à une classe connue."""
        template = self.known_templates.get(class_name, "")
        return template.format(scenario_text=scenario_text, class_name=class_name)


DEFAULT_TEMPLATES: Dict[str, str] = {
    "App": textwrap.dedent(
        '''\
        """Scénario généré par gabarit pour la classe App.

        Scénario : {scenario_text}
        """


        def run_scenario() -> None:
            print("Exécution du scénario App : {scenario_text}")
            print("Classe cible : {class_name}")


        if __name__ == "__main__":
            run_scenario()
        '''
    ),
}


class FlyncMasterAgent:
    """
    Agent Maître : orchestre la séquence macro complète du pipeline FLYNC,
    de l'analyse AST parallèle jusqu'à la production du rapport final.
    """

    def __init__(
        self,
        search_paths: Sequence[str],
        target_modules: Optional[Sequence[str]] = None,
        max_analysis_workers: Optional[int] = None,
        max_retries_per_scenario: int = 3,
        rag_high_threshold: float = 0.5,
        rag_low_threshold: float = 0.15,
        use_embeddings: bool = False,
        developer_client: Optional[AnthropicDeveloperClient] = None,
        dispatch_heuristic: Optional[ModeDispatchHeuristic] = None,
        lecteur_agent: Optional[AgentLecteurAnalyste] = None,
    ) -> None:
        # search_paths n'est plus utilisé pour localiser les modules (l'agent
        # lecteur se connecte a la KB via kb_pointers.py et clone/synchronise
        # le depot lui-meme) : conserve pour compatibilite CLI et pour
        # d'eventuels usages futurs de recherche locale complementaire.
        self.search_paths = list(search_paths)
        self.target_modules = list(target_modules) if target_modules else None
        self.max_analysis_workers = max_analysis_workers
        self.max_retries_per_scenario = max_retries_per_scenario
        self.rag_high_threshold = rag_high_threshold
        self.rag_low_threshold = rag_low_threshold
        self.use_embeddings = use_embeddings
        self.developer_client = developer_client
        self.dispatch_heuristic = dispatch_heuristic or ModeDispatchHeuristic(DEFAULT_TEMPLATES)
        self.lecteur_agent = lecteur_agent or AgentLecteurAnalyste()

        self.knowledge_base: Optional[KBAnalysisReport] = None
        self.relation_graph: Optional[ModuleRelationGraph] = None
        self.retriever: Optional[HybridKBRetriever] = None
        self.verifier: Optional[ScenarioVerifier] = None

    # ------------------------------------------------------------------ #
    # Étapes du pipeline macro
    # ------------------------------------------------------------------ #

    def step_1_analyze_kb_parallel(self) -> KBAnalysisReport:
        """Étape 1 : analyse AST parallèle des modules FLYNC (via
        AgentLecteurAnalyste, qui gère elle-même son parallélisme interne
        avec ProcessPoolExecutor / repli ThreadPoolExecutor)."""
        logger.info(
            "Étape 1/5 — Analyse KB parallèle (%s)...",
            f"{len(self.target_modules)} module(s) ciblé(s)" if self.target_modules else "tous modules découverts",
        )
        kb = self.lecteur_agent.run(
            target_modules=self.target_modules,
            max_workers=self.max_analysis_workers,
        )
        logger.info(
            "Étape 1/5 terminée : %d classes indexées, %d erreur(s) de module.",
            len(kb.all_classes()),
            len(kb.errors),
        )
        self.knowledge_base = kb
        return kb

    def step_2_build_dependency_graph(self) -> ModuleRelationGraph:
        """Étape 2 : construction du ModuleRelationGraph."""
        if self.knowledge_base is None:
            raise RuntimeError("step_1_analyze_kb_parallel() doit être appelée avant l'étape 2.")
        logger.info("Étape 2/5 — Construction du graphe de dépendances...")
        graph = build_module_relation_graph(self.knowledge_base)
        logger.info(
            "Étape 2/5 terminée : %d noeuds, cycle détecté=%s.",
            len(graph.nodes),
            graph.has_cycle(),
        )
        self.relation_graph = graph
        return graph

    def step_3_index_retriever(self) -> HybridKBRetriever:
        """Étape 3 : indexation des classes dans le Retriever Hybride."""
        if self.knowledge_base is None:
            raise RuntimeError("step_1_analyze_kb_parallel() doit être appelée avant l'étape 3.")
        logger.info("Étape 3/5 — Indexation & retrieval hybride...")
        retriever = HybridKBRetriever(use_embeddings=self.use_embeddings)
        retriever.index_classes(self.knowledge_base.all_classes())
        logger.info(
            "Étape 3/5 terminée : %d classes indexées dans le retriever.",
            retriever.indexed_class_count,
        )
        self.retriever = retriever
        return retriever

    def step_4_build_verifier(self) -> ScenarioVerifier:
        """Étape 4 : construction du ScenarioVerifier (alias + RAG fallback)."""
        if self.knowledge_base is None or self.retriever is None:
            raise RuntimeError(
                "Les étapes 1 et 3 doivent être exécutées avant l'étape 4."
            )
        logger.info("Étape 4/5 — Construction du ScenarioVerifier...")
        verifier = ScenarioVerifier(
            knowledge_base=self.knowledge_base,
            retriever=self.retriever,
            rag_high_threshold=self.rag_high_threshold,
            rag_low_threshold=self.rag_low_threshold,
        )
        logger.info("Étape 4/5 terminée : ScenarioVerifier prêt.")
        self.verifier = verifier
        return verifier

    def _build_class_context(self, cls: ClassInfo) -> str:
        field_lines = "\n".join(
            f"  - {f.name}: {f.type_str}" + ("" if f.required else f" (optionnel, défaut: {f.default_str})")
            for f in cls.fields
        ) or "  (aucun champ détecté)"
        validator_lines = ", ".join(v.method_name for v in cls.validators) or "(aucun validateur détecté)"
        enum_note = ""
        if cls.is_enum:
            enum_note = (
                f"\n            ATTENTION: '{cls.name}' est un Enum — il se REFERENCE par "
                f"un de ses membres ({cls.name}.{cls.enum_members[0] if cls.enum_members else '...'}), "
                f"il ne se CONSTRUIT jamais comme un modèle.\n"
                f"            Membres: {', '.join(cls.enum_members) or '(aucun détecté)'}"
            )
        return textwrap.dedent(
            f"""\
            Module: {cls.module}
            Classe: {cls.name}
            Bases: {', '.join(cls.bases) or '(aucune)'}
            Docstring: {cls.docstring or '(absente)'}
            Champs:
            {field_lines}
            Validateurs: {validator_lines}{enum_note}
            """
        )

    def step_5_dispatch_and_run(self, scenarios: Sequence[str]) -> List[ScenarioOutcome]:
        """
        Étape 5 : pour chaque scénario, résout la classe cible via le
        ScenarioVerifier, choisit le mode de génération (template/llm) via
        l'heuristique de dispatch, puis exécute la génération correspondante
        (gabarit direct, ou boucle LangGraph complète pour le mode llm).
        """
        if self.verifier is None:
            raise RuntimeError("step_4_build_verifier() doit être appelée avant l'étape 5.")

        logger.info("Étape 5/5 — Dispatch et exécution de %d scénario(s)...", len(scenarios))
        outcomes: List[ScenarioOutcome] = []
        langgraph_orchestrator: Optional[ScenarioLangGraphOrchestrator] = None

        for idx, scenario_text in enumerate(scenarios):
            scenario_id = f"scenario_{idx + 1:03d}"
            start = time.perf_counter()

            resolution = self.verifier.resolve(scenario_text)
            mode = self.dispatch_heuristic.decide(resolution)

            logger.info(
                "[%s] Résolution=%s confiance=%s mode=%s",
                scenario_id,
                resolution.resolved_class.name if resolution.resolved_class else "AUCUNE",
                resolution.confidence.value,
                mode.value,
            )

            if resolution.resolved_class is None:
                outcomes.append(
                    ScenarioOutcome(
                        scenario_id=scenario_id,
                        scenario_text=scenario_text,
                        resolved_class_name=None,
                        resolved_module=None,
                        confidence=resolution.confidence.value,
                        dispatch_mode=mode.value,
                        status="FAILURE",
                        notes=["Aucune classe résolue : impossible de générer du code."],
                        duration_seconds=time.perf_counter() - start,
                    )
                )
                continue

            if mode == DispatchMode.TEMPLATE:
                code = self.dispatch_heuristic.render_template(
                    resolution.resolved_class.name, scenario_text
                )
                outcomes.append(
                    ScenarioOutcome(
                        scenario_id=scenario_id,
                        scenario_text=scenario_text,
                        resolved_class_name=resolution.resolved_class.name,
                        resolved_module=resolution.resolved_class.module,
                        confidence=resolution.confidence.value,
                        dispatch_mode=mode.value,
                        status="SUCCESS",
                        generated_code=code,
                        retry_count=0,
                        duration_seconds=time.perf_counter() - start,
                        notes=["Génération par gabarit, aucun appel LLM effectué."],
                    )
                )
                continue

            # Mode LLM : dispatch vers la boucle micro LangGraph.
            if langgraph_orchestrator is None:
                langgraph_orchestrator = ScenarioLangGraphOrchestrator(
                    developer_client=self.developer_client or AnthropicDeveloperClient(),
                    max_retries=self.max_retries_per_scenario,
                )

            class_context = self._build_class_context(resolution.resolved_class)
            final_state = langgraph_orchestrator.run_scenario(
                scenario_id=scenario_id,
                scenario_text=scenario_text,
                target_class_name=resolution.resolved_class.name,
                target_class_context=class_context,
                confidence=resolution.confidence.value,
                max_retries=self.max_retries_per_scenario,
            )

            outcomes.append(
                ScenarioOutcome(
                    scenario_id=scenario_id,
                    scenario_text=scenario_text,
                    resolved_class_name=resolution.resolved_class.name,
                    resolved_module=resolution.resolved_class.module,
                    confidence=resolution.confidence.value,
                    dispatch_mode=mode.value,
                    status=final_state.get("status", "FAILURE"),
                    generated_code=final_state.get("generated_code", ""),
                    retry_count=final_state.get("retry_count", 0),
                    duration_seconds=time.perf_counter() - start,
                    notes=[final_state.get("evaluation_notes", "")],
                )
            )

        logger.info("Étape 5/5 terminée : %d scénario(s) traité(s).", len(outcomes))
        return outcomes

    # ------------------------------------------------------------------ #
    # Exécution complète du pipeline
    # ------------------------------------------------------------------ #

    def run(self, scenarios: Sequence[str]) -> PipelineReport:
        """
        Exécute la séquence macro complète (étapes 1 à 5) et retourne le
        rapport global du pipeline.
        """
        pipeline_start = time.perf_counter()

        self.step_1_analyze_kb_parallel()
        self.step_2_build_dependency_graph()
        self.step_3_index_retriever()
        self.step_4_build_verifier()
        outcomes = self.step_5_dispatch_and_run(scenarios)

        assert self.knowledge_base is not None
        assert self.relation_graph is not None

        report = PipelineReport(
            total_modules_analyzed=len(self.knowledge_base.modules),
            total_classes_indexed=len(self.knowledge_base.all_classes()),
            module_analysis_errors=dict(self.knowledge_base.errors),
            topological_module_order=self.relation_graph.topological_order(),
            outcomes=outcomes,
            total_duration_seconds=time.perf_counter() - pipeline_start,
        )
        return report


# --------------------------------------------------------------------------- #
# Point d'entrée CLI
# --------------------------------------------------------------------------- #

def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline FLYNC — orchestrateur principal (Agent Maître)."
    )
    parser.add_argument(
        "--search-path",
        action="append",
        dest="search_paths",
        default=None,
        help="Répertoire racine où chercher les modules FLYNC (répétable).",
    )
    parser.add_argument(
        "--scenarios-file",
        type=str,
        default=None,
        help="Chemin vers un fichier texte contenant un scénario par ligne.",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenarios",
        default=None,
        help="Scénario unique en ligne de commande (répétable).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Nombre maximal de tentatives de correction par scénario en mode LLM.",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=None,
        help="Chemin de sortie pour le rapport JSON du pipeline.",
    )
    parser.add_argument(
        "--use-embeddings",
        action="store_true",
        help="Active le backend d'embeddings Ollama pour le retriever hybride.",
    )
    return parser.parse_args(argv)


def _load_scenarios(args: argparse.Namespace) -> List[str]:
    scenarios: List[str] = []
    if args.scenarios:
        scenarios.extend(args.scenarios)
    if args.scenarios_file:
        with open(args.scenarios_file, "r", encoding="utf-8") as fh:
            scenarios.extend(line.strip() for line in fh if line.strip())
    return scenarios


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    scenarios = _load_scenarios(args)

    if not scenarios:
        logger.error(
            "Aucun scénario fourni. Utilisez --scenario ou --scenarios-file."
        )
        return 1

    search_paths = args.search_paths or ["."]

    agent = FlyncMasterAgent(
        search_paths=search_paths,
        max_retries_per_scenario=args.max_retries,
        use_embeddings=args.use_embeddings,
    )
    report = agent.run(scenarios)

    print(report.summary())

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as fh:
            json.dump(report.to_dict(), fh, ensure_ascii=False, indent=2)
        logger.info("Rapport JSON écrit dans %s", args.output_json)

    return 0 if all(o.status == "SUCCESS" for o in report.outcomes) else 2


if __name__ == "__main__":
    sys.exit(main())
"""
Orchestrator -- toutes les etapes du pipeline dans un seul fichier.

1. Fan-out: les 11 agents submodel tournent (Actor Positive-only -> Critic
   audit+mutation vers Negative)
2. Deduplicate: fusionne les resultats, supprime les quasi-doublons
   (embeddings + cosine similarity)
3. Cross-module (base sur le VRAI graphe de code, pas des paires forcees):
   - Positive + Dangling pour chaque relation reelle trouvee dans le code
     source (via graph_builder/extract_relations.py, extraction ast)
   - Isolation pour les paires de submodels SANS relation reelle
   - Plafonne le nombre total d'appels LLM (defaut 60, pour tenir dans
     3 cles Gemini x 20 requetes/jour)
"""
from __future__ import annotations
from typing import TypedDict, Annotated
import itertools
import json
import re

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END

from phase1.schemas.scenario_schema import Scenario, validate_scenario, ScenarioValidationError
from phase1.retriever.doc_retriever import get_relevant_chunks
from phase1.graph_builder.extract_relations import load_relation_graph

from phase1.agents import (
    tsn_agent,
)
from phase1.agents import app_agent, bus_agent, communication_agent, ecu_agent, metadata_agent, nm_agent, security_agent, signal_agent, someip_agent, topology_agent

AGENT_MODULES = [
    app_agent, bus_agent, communication_agent, ecu_agent, metadata_agent,
    nm_agent, security_agent, signal_agent, someip_agent, topology_agent, tsn_agent,
]

DEDUP_SIMILARITY_THRESHOLD = 0.85
MAX_GRAPH_CALLS = 55  # 3 Gemini keys x 20 req/day


def _merge_dicts(a: dict, b: dict) -> dict:
    """Reducer: lets parallel agent nodes each write their own key of
    scenarios_by_module without clobbering each other."""
    return {**a, **b}


class PipelineState(TypedDict):
    scenarios_by_module: Annotated[dict[str, list[Scenario]], _merge_dicts]
    merged_scenarios: list[Scenario]
    cross_module_scenarios: list[Scenario]


# ---------------------------------------------------------------------------
# Etape 1 -- Fan-out des 11 agents (Actor Positive-only -> Critic mutation)
# ---------------------------------------------------------------------------
def _make_agent_node(agent_module):
    """Retourne une fonction-noeud LangGraph qui lance un agent submodel."""
    def node(state: PipelineState, llm_router) -> dict:
        agent = agent_module.build_agent(llm_router)
        scenarios = agent.generate_scenarios(n_scenarios=10)
        return {"scenarios_by_module": {agent.submodel_name: scenarios}}
    return node


# ---------------------------------------------------------------------------
# Etape 2 -- Deduplication (embeddings + cosine similarity)
# ---------------------------------------------------------------------------
_embedding_model = None


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def _deduplicate_scenarios(scenarios: list[Scenario], protect_key=None) -> list[Scenario]:
    """Supprime les quasi-doublons par similarite d'embeddings.

    Si protect_key est fourni (fonction scenario -> str), au moins un
    scenario par valeur de cle distincte est TOUJOURS garde -- meme s'il
    ressemble a un doublon -- pour ne jamais faire perdre la couverture
    d'un submodel/paire specifique.
    """
    if not scenarios:
        return []

    model = _get_embedding_model()
    texts = [f"{s.title}. {s.description}" for s in scenarios]
    embeddings = model.encode(texts, show_progress_bar=False)
    sim_matrix = cosine_similarity(embeddings)

    covered_keys: set[str] = set()
    kept_indices: list[int] = []
    for i in range(len(scenarios)):
        key = protect_key(scenarios[i]) if protect_key else None
        must_keep_for_coverage = key is not None and key not in covered_keys
        is_duplicate = any(
            sim_matrix[i][j] >= DEDUP_SIMILARITY_THRESHOLD for j in kept_indices
        )
        if not is_duplicate or must_keep_for_coverage:
            kept_indices.append(i)
            if key is not None:
                covered_keys.add(key)

    return [scenarios[i] for i in kept_indices]


def deduplicate_node(state: PipelineState) -> dict:
    all_scenarios: list[Scenario] = []
    for scenarios in state["scenarios_by_module"].values():
        all_scenarios.extend(scenarios)

    kept = _deduplicate_scenarios(all_scenarios)
    print(f"[orchestrator] Deduplication: {len(all_scenarios)} -> {len(kept)} scenarios")
    return {"merged_scenarios": kept}


# ---------------------------------------------------------------------------
# Etape 3 -- Cross-module base sur le graphe REEL du code source
# ---------------------------------------------------------------------------
POSITIVE_PROMPT_TEMPLATE = """You are a senior test engineer writing a cross-module test
scenario for the FLYNC automotive network configuration model.

REAL relation found in the source code (not invented): the class
"{src_class}" in submodel "{src_domain}" has a field "{field_name}" whose
type references the class "{dst_class}" in submodel "{dst_domain}".

Relevant documentation excerpts for context:
{contexts}

TASK: Generate exactly 1 Positive test scenario that configures this exact
relation VALIDLY -- both {src_class} and {dst_class} are properly defined,
and {src_class}.{field_name} correctly resolves to a valid {dst_class}
instance.
- "description" must name {src_class}, {field_name}, and {dst_class} explicitly
- "expected_result" must state that validation succeeds because the
  reference resolves correctly
- Use "submodel" field exactly as: "cross_module ({src_domain} + {dst_domain})"

Return ONLY a JSON array with exactly one object, no prose, no markdown fences:
[
  {{"id": "PLACEHOLDER", "submodel": "cross_module ({src_domain} + {dst_domain})",
    "type": "Positive", "title": "string", "description": "string",
    "injected_fault": null, "expected_result": "string"}}
]
"""

DANGLING_PROMPT_TEMPLATE = """You are a senior test engineer writing a cross-module test
scenario for the FLYNC automotive network configuration model.

REAL relation found in the source code (not invented): the class
"{src_class}" in submodel "{src_domain}" has a field "{field_name}" whose
type references the class "{dst_class}" in submodel "{dst_domain}".

Relevant documentation excerpts for context:
{contexts}

TASK: Generate exactly 1 Negative test scenario using a DANGLING REFERENCE
fault: {src_class}.{field_name} is configured to reference a {dst_class}
identifier, but that {dst_class} instance is completely absent from the
{dst_domain} configuration (removed/never defined).
- "description" must name {src_class}, {field_name}, and {dst_class} explicitly,
  and state that the referenced instance does not exist
- "injected_fault" must describe this exact dangling reference concretely
- "expected_result" must state that validation fails with a dangling/unresolved
  reference error
- Use "submodel" field exactly as: "cross_module ({src_domain} + {dst_domain})"

Return ONLY a JSON array with exactly one object, no prose, no markdown fences:
[
  {{"id": "PLACEHOLDER", "submodel": "cross_module ({src_domain} + {dst_domain})",
    "type": "Negative", "title": "string", "description": "string",
    "injected_fault": "string", "expected_result": "string"}}
]
"""

ISOLATION_PROMPT_TEMPLATE = """You are a senior test engineer writing a cross-module test
scenario for the FLYNC automotive network configuration model.

IMPORTANT: analysis of the real source code found NO relation whatsoever
between submodel "{domain_a}" and submodel "{domain_b}" -- no class in
either domain references a class from the other. These two domains are
architecturally isolated from each other.

Relevant documentation excerpts for context:
{contexts}

TASK: Generate exactly 1 Negative test scenario using an ISOLATION BREACH
fault: a configuration is written that creates a DIRECT reference or
dependency between a class in "{domain_a}" and a class in "{domain_b}" --
something that should never happen given these domains have no legitimate
architectural relationship.
- "description" must name specific (real, documented) classes from BOTH
  domains and describe the illegitimate direct link between them
- "injected_fault" must describe this cross-domain isolation breach concretely
- "expected_result" must state that validation fails, rejecting the
  illegitimate cross-domain reference
- Use "submodel" field exactly as: "cross_module ({domain_a} + {domain_b})"

Return ONLY a JSON array with exactly one object, no prose, no markdown fences:
[
  {{"id": "PLACEHOLDER", "submodel": "cross_module ({domain_a} + {domain_b})",
    "type": "Negative", "title": "string", "description": "string",
    "injected_fault": "string", "expected_result": "string"}}
]
"""


def _parse_evidence(evidence_str: str) -> tuple[str, str, str]:
    """"ECU.ecu_metadata -> ECUMetadata" -> ("ECU", "ecu_metadata", "ECUMetadata")"""
    left, dst_class = [s.strip() for s in evidence_str.split("->")]
    src_class, field_name = left.split(".", 1)
    return src_class, field_name, dst_class


def _run_graph_llm_call(prompt: str, llm_router, scenario_id: str, expected_submodel: str) -> list[Scenario]:
    raw = llm_router.call_integrator(prompt)
    cleaned = re.sub(r"```json|```", "", raw).strip()
    scenarios = []
    try:
        for item in json.loads(cleaned):
            item["id"] = scenario_id  # jamais confier l'id au LLM
            item["submodel"] = expected_submodel  # jamais confier le format au LLM non plus
            try:
                scenarios.append(validate_scenario(item))
            except ScenarioValidationError as e:
                print(f"[graph_cross_module] dropped invalid scenario ({scenario_id}): {e}")
    except json.JSONDecodeError:
        print(f"[graph_cross_module] failed to parse LLM output for {scenario_id}")
    return scenarios


def _generate_positive_scenario(src_domain, dst_domain, evidence_str, llm_router, idx) -> list[Scenario]:
    src_class, field_name, dst_class = _parse_evidence(evidence_str)
    contexts = f"--- {src_domain} ---\n{get_relevant_chunks(src_domain)[:1200]}\n\n--- {dst_domain} ---\n{get_relevant_chunks(dst_domain)[:1200]}"
    prompt = POSITIVE_PROMPT_TEMPLATE.format(
        src_class=src_class, field_name=field_name, dst_class=dst_class,
        src_domain=src_domain, dst_domain=dst_domain, contexts=contexts,
    )
    expected_submodel = f"cross_module ({src_domain} + {dst_domain})"
    return _run_graph_llm_call(prompt, llm_router, f"SC-GRAPH-POS-{idx:03d}", expected_submodel)


def _generate_dangling_scenario(src_domain, dst_domain, evidence_str, llm_router, idx) -> list[Scenario]:
    src_class, field_name, dst_class = _parse_evidence(evidence_str)
    contexts = f"--- {src_domain} ---\n{get_relevant_chunks(src_domain)[:1200]}\n\n--- {dst_domain} ---\n{get_relevant_chunks(dst_domain)[:1200]}"
    prompt = DANGLING_PROMPT_TEMPLATE.format(
        src_class=src_class, field_name=field_name, dst_class=dst_class,
        src_domain=src_domain, dst_domain=dst_domain, contexts=contexts,
    )
    expected_submodel = f"cross_module ({src_domain} + {dst_domain})"
    return _run_graph_llm_call(prompt, llm_router, f"SC-GRAPH-DANGLING-{idx:03d}", expected_submodel)


def _generate_isolation_scenario(domain_a, domain_b, llm_router, idx) -> list[Scenario]:
    contexts = f"--- {domain_a} ---\n{get_relevant_chunks(domain_a)[:1200]}\n\n--- {domain_b} ---\n{get_relevant_chunks(domain_b)[:1200]}"
    prompt = ISOLATION_PROMPT_TEMPLATE.format(domain_a=domain_a, domain_b=domain_b, contexts=contexts)
    expected_submodel = f"cross_module ({domain_a} + {domain_b})"
    return _run_graph_llm_call(prompt, llm_router, f"SC-GRAPH-ISOLATION-{idx:03d}", expected_submodel)


def make_cross_module_node(llm_router):
    def node(state: PipelineState) -> dict:
        graph = load_relation_graph()
        all_scenarios: list[Scenario] = []
        calls_made = 0

        # Priorite 1: Positive + Dangling pour chaque relation reelle
        idx = 0
        for src, dst, data in graph.edges(data=True):
            if calls_made + 2 > MAX_GRAPH_CALLS:
                print(f"[orchestrator] Budget cross-module atteint ({calls_made}/{MAX_GRAPH_CALLS}) -- arret des aretes")
                break
            evidence = data["evidence"][0]
            idx += 1
            pos = _generate_positive_scenario(src, dst, evidence, llm_router, idx)
            neg = _generate_dangling_scenario(src, dst, evidence, llm_router, idx)
            calls_made += 2
            print(f"[orchestrator] Edge {src} -> {dst}: {len(pos)} positive, {len(neg)} dangling ({calls_made}/{MAX_GRAPH_CALLS})")
            all_scenarios.extend(pos)
            all_scenarios.extend(neg)

        # Priorite 2: Isolation -- seulement dans le budget restant
        domains = sorted(graph.nodes())
        connected_pairs = {frozenset((u, v)) for u, v in graph.edges()}
        isolated_pairs = [
            (a, b) for a, b in itertools.combinations(domains, 2)
            if frozenset((a, b)) not in connected_pairs
        ]
        remaining_budget = MAX_GRAPH_CALLS - calls_made
        selected_isolated_pairs = isolated_pairs[:remaining_budget]
        if remaining_budget < len(isolated_pairs):
            print(f"[orchestrator] {remaining_budget} places pour {len(isolated_pairs)} paires isolees -- echantillon de {remaining_budget}")

        for iso_idx, (domain_a, domain_b) in enumerate(selected_isolated_pairs, start=1):
            iso = _generate_isolation_scenario(domain_a, domain_b, llm_router, iso_idx)
            calls_made += 1
            print(f"[orchestrator] Isolation {domain_a} <-> {domain_b}: {len(iso)} scenarios ({calls_made}/{MAX_GRAPH_CALLS})")
            all_scenarios.extend(iso)

        # Dedup finale du cross-module, en protegeant la couverture par paire
        deduped = _deduplicate_scenarios(all_scenarios, protect_key=lambda s: s.submodel)
        print(f"[orchestrator] Cross-module: {calls_made} appels LLM, {len(all_scenarios)} -> {len(deduped)} scenarios apres dedup")
        return {"cross_module_scenarios": deduped}
    return node


# ---------------------------------------------------------------------------
# Assemblage du graphe LangGraph
# ---------------------------------------------------------------------------
def build_graph(llm_router):
    graph = StateGraph(PipelineState)

    for agent_module in AGENT_MODULES:
        node_name = agent_module.__name__.split(".")[-1]
        node_fn = _make_agent_node(agent_module)
        graph.add_node(node_name, lambda state, fn=node_fn: fn(state, llm_router))
        graph.add_edge("__start__", node_name)
        graph.add_edge(node_name, "deduplicate")

    graph.add_node("deduplicate", deduplicate_node)
    graph.add_node("cross_module", make_cross_module_node(llm_router))
    graph.add_edge("deduplicate", "cross_module")
    graph.add_edge("cross_module", END)

    return graph.compile()


def run_pipeline(llm_router) -> list[Scenario]:
    app = build_graph(llm_router)
    initial_state: PipelineState = {
        "scenarios_by_module": {},
        "merged_scenarios": [],
        "cross_module_scenarios": [],
    }
    # max_concurrency=1: les agents tournent sequentiellement, un par un
    final_state = app.invoke(initial_state, config={"max_concurrency": 1})
    return final_state["merged_scenarios"] + final_state["cross_module_scenarios"]
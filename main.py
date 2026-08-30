"""
Entry point -- Team 1 scenario generation.

Pipeline:
  1. Refresh FLYNC docs automatically if the GitHub cache is stale
  2. Refresh FLYNC source code automatically (for the relation graph)
     and rebuild the graph if the source changed
  3. Build the LLMRouter (Groq generator+critic, Gemini integrator)
  4. Run the orchestrator (11 agents -> dedup -> graph-based cross-module)
  5. Write the consolidated result to output/scenarios.json
"""
import os
import time
import json
import requests
from collections import Counter
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

SUBMODELS_OUTPUT_PATH = "output/scenarios_submodels.json"
CROSS_MODULE_OUTPUT_PATH = "output/scenarios_cross_module.json"

REPO_OWNER = "Technica-Engineering"
REPO_NAME = "FLYNC"
REPO_BRANCH = "main"
DOCS_SOURCE_PATH = "docs/source/flync_reference/submodels"

LOCAL_DOCS_DIR = "data/flync_docs"
LAST_COMMIT_FILE = "data/.last_commit"
LAST_CHECK_TIME_FILE = LAST_COMMIT_FILE + ".checked_at"
CHECK_INTERVAL_HOURS = 6

GITHUB_API_BASE = "https://api.github.com"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com"


def _github_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _last_check_too_recent() -> bool:
    if not os.path.exists(LAST_CHECK_TIME_FILE):
        return False
    with open(LAST_CHECK_TIME_FILE) as f:
        last_check = float(f.read().strip() or 0)
    return (time.time() - last_check) / 3600 < CHECK_INTERVAL_HOURS


def refresh_docs_if_needed() -> bool:
    """Etape 1: verification de fraicheur automatique + telechargement
    conditionnel de la doc. Throttle a CHECK_INTERVAL_HOURS."""
    if _last_check_too_recent():
        print("[main] Freshness check skipped (checked recently) -- using local cache.")
        return False

    url = (
        f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/commits"
        f"?sha={REPO_BRANCH}&path={DOCS_SOURCE_PATH}&per_page=1"
    )
    resp = requests.get(url, headers=_github_headers(), timeout=15)
    resp.raise_for_status()
    latest_sha = resp.json()[0]["sha"]

    os.makedirs(os.path.dirname(LAST_CHECK_TIME_FILE), exist_ok=True)
    with open(LAST_CHECK_TIME_FILE, "w") as f:
        f.write(str(time.time()))

    cached_sha = None
    if os.path.exists(LAST_COMMIT_FILE):
        with open(LAST_COMMIT_FILE) as f:
            cached_sha = f.read().strip() or None

    if latest_sha == cached_sha:
        print(f"[main] Docs up to date (commit {latest_sha[:7]}) -- using local cache.")
        return False

    print(f"[main] Docs changed (commit {latest_sha[:7]}) -- downloading...")
    list_url = f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{DOCS_SOURCE_PATH}?ref={REPO_BRANCH}"
    entries = requests.get(list_url, headers=_github_headers(), timeout=15).json()

    os.makedirs(LOCAL_DOCS_DIR, exist_ok=True)
    for entry in entries:
        if entry["type"] != "file":
            continue
        raw_url = f"{GITHUB_RAW_BASE}/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}/{DOCS_SOURCE_PATH}/{entry['name']}"
        content = requests.get(raw_url, timeout=15).text
        with open(os.path.join(LOCAL_DOCS_DIR, entry["name"]), "w", encoding="utf-8") as f:
            f.write(content)

    with open(LAST_COMMIT_FILE, "w") as f:
        f.write(latest_sha)
    print(f"[main] Downloaded {len(entries)} doc files.")
    return True


def refresh_source_and_graph_if_needed() -> None:
    """Etape 2: rafraichit le code source FLYNC (meme mecanisme de
    fraicheur que pour la doc) et reconstruit le graphe de relations
    (ast, pas de cout LLM) UNIQUEMENT si le source a change."""
    from graph_builder.download_source import refresh_source_if_needed
    from graph_builder.extract_relations import (
        build_class_index, build_relation_graph, save_class_index, save_relation_graph,
    )

    source_changed = refresh_source_if_needed()
    if source_changed:
        print("[main] Source code changed -- rebuilding relation graph...")
        class_index = build_class_index()
        graph = build_relation_graph(class_index)
        save_class_index(class_index)
        save_relation_graph(graph)
        print(f"[main] Graph rebuilt: {graph.number_of_nodes()} domains, {graph.number_of_edges()} relations.")
    else:
        print("[main] Source code up to date -- reusing cached relation graph.")


def _get_flync_commit_sha() -> str | None:
    if not os.path.exists(LAST_COMMIT_FILE):
        return None
    with open(LAST_COMMIT_FILE) as f:
        return f.read().strip() or None


def _validate_and_report(scenarios) -> None:
    """Derniere passe de controle avant l'ecriture du livrable."""
    from graph_builder.extract_relations import load_relation_graph

    print("\n[main] === Validation report ===")

    ids = [s.id for s in scenarios]
    duplicate_ids = {i for i in ids if ids.count(i) > 1}
    if duplicate_ids:
        print(f"[main] WARNING: duplicate IDs found: {sorted(duplicate_ids)}")
    else:
        print(f"[main] OK: all {len(ids)} scenario IDs are unique")

    cross_module_pairs_covered = {s.submodel for s in scenarios if s.submodel.startswith("cross_module")}
    graph = load_relation_graph()
    total_real_edges = graph.number_of_edges()
    print(f"[main] Cross-module pairs covered: {len(cross_module_pairs_covered)} "
          f"(real relations in graph: {total_real_edges})")

    type_counts = Counter(s.type.value for s in scenarios)
    print(f"[main] Type distribution: {dict(type_counts)}")
    print("[main] === End of validation report ===\n")


def _build_stats(scenarios) -> dict:
    """Statistiques communes reutilisees pour les deux fichiers."""
    type_counts = Counter(s.type.value for s in scenarios)
    per_submodel_counts: dict[str, int] = {}
    for s in scenarios:
        per_submodel_counts[s.submodel] = per_submodel_counts.get(s.submodel, 0) + 1
    return {
        "total_scenarios": len(scenarios),
        "type_distribution": dict(type_counts),
        "scenario_count_per_submodel": per_submodel_counts,
    }


def write_submodels_output(scenarios) -> None:
    """Fichier 1: uniquement les scenarios par submodel (Positive + leurs
    Negative mutes), avec leurs propres statistiques."""
    submodel_scenarios = [s for s in scenarios if not s.submodel.startswith("cross_module")]
    os.makedirs(os.path.dirname(SUBMODELS_OUTPUT_PATH), exist_ok=True)

    stats = _build_stats(submodel_scenarios)
    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "flync_commit_sha": _get_flync_commit_sha(),
            **stats,
            "submodels_covered": sorted({s.submodel for s in submodel_scenarios}),
        },
        "scenarios": [s.to_dict() for s in submodel_scenarios],
    }
    with open(SUBMODELS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[main] Wrote {len(submodel_scenarios)} submodel scenarios to {SUBMODELS_OUTPUT_PATH}")


def write_cross_module_output(scenarios) -> None:
    """Fichier 2: uniquement les scenarios cross-module (Positive/Dangling/
    Isolation issus du graphe reel), avec leurs propres statistiques."""
    from graph_builder.extract_relations import load_relation_graph

    cross_scenarios = [s for s in scenarios if s.submodel.startswith("cross_module")]
    os.makedirs(os.path.dirname(CROSS_MODULE_OUTPUT_PATH), exist_ok=True)

    graph = load_relation_graph()
    stats = _build_stats(cross_scenarios)
    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "flync_commit_sha": _get_flync_commit_sha(),
            **stats,
            "real_relations_in_graph": graph.number_of_edges(),
            "domains_in_graph": graph.number_of_nodes(),
            "pairs_covered": sorted({s.submodel for s in cross_scenarios}),
        },
        "scenarios": [s.to_dict() for s in cross_scenarios],
    }
    with open(CROSS_MODULE_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[main] Wrote {len(cross_scenarios)} cross-module scenarios to {CROSS_MODULE_OUTPUT_PATH}")


def main():
    from agents.llm_router import LLMRouter
    from orchestrator.graph import run_pipeline

    print("[main] Step 1: checking FLYNC docs freshness...")
    refresh_docs_if_needed()

    print("[main] Step 2: checking FLYNC source code freshness (for relation graph)...")
    refresh_source_and_graph_if_needed()

    print("[main] Step 3: building LLM router (Groq Actor / Groq Critic / Gemini Integrator)...")
    llm_router = LLMRouter()

    print("[main] Step 4: running the pipeline (11 agents -> dedup -> graph-based cross-module)...")
    scenarios = run_pipeline(llm_router)

    _validate_and_report(scenarios)

    print("[main] Step 5: writing output (2 files: submodels + cross-module)...")
    write_submodels_output(scenarios)
    write_cross_module_output(scenarios)


if __name__ == "__main__":
    main()
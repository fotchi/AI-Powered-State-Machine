"""
Parser FLYNC — Etape 1: telechargement du vrai code source, avec le meme
mecanisme de fraicheur que pour la doc (retriever/doc_retriever.py) :
  1. Compare le dernier commit GitHub touchant src/flync/model/ au commit
     stocke localement
  2. Ne re-telecharge que si ca a change (throttle : ne verifie meme pas
     si le dernier check date de moins de CHECK_INTERVAL_HOURS)
  3. Telecharge tout le contenu reel de chaque dossier de domaine via le
     Git Trees API (pas de suivi d'imports -- rate un fichier importe
     seulement de facon transitive par un autre fichier du domaine sinon)
"""
import os
import time
import requests

DOMAINS = [
    "flync_4_app", "flync_4_bus", "flync_4_communication", "flync_4_diagnostics",
    "flync_4_ecu", "flync_4_metadata", "flync_4_nm", "flync_4_safety", "flync_4_security",
    "flync_4_signal", "flync_4_someip", "flync_4_topology", "flync_4_tsn",
]
# flync_4_diagnostics has no scenario-generation agent of its own (see
# single_run.py::AGENTS_BY_KEY, still 11 submodels) -- it's listed here only
# because flync_4_ecu/sockets.py imports from it, and without its files on
# disk that import fails at execution time for any ECU scenario touching
# sockets/endpoints. Downloading it costs nothing extra we don't already need.

REPO_OWNER = "Technica-Engineering"
REPO_NAME = "FLYNC"
REPO_BRANCH = "main"
SOURCE_PATH = "src/flync/model"
CORE_PATH = "src/flync/core"

OUTPUT_DIR = "data/flync_source"
LAST_COMMIT_FILE = f"{OUTPUT_DIR}/.last_commit"
LAST_CHECK_TIME_FILE = LAST_COMMIT_FILE + ".checked_at"
CHECK_INTERVAL_HOURS = 6

# flync/core/** (validators, base models, datatypes, utils) -- every class
# under model/ imports from here, so phase2 needs it too in order to
# actually EXECUTE the scripts it generates, not just to statically
# analyze the model/ files (see download_core_package() below).
CORE_OUTPUT_DIR = "data/flync_core"
CORE_LAST_COMMIT_FILE = f"{CORE_OUTPUT_DIR}/.last_commit"
CORE_LAST_CHECK_TIME_FILE = CORE_LAST_COMMIT_FILE + ".checked_at"

GITHUB_API_BASE = "https://api.github.com"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}/{SOURCE_PATH}"
RAW_ROOT_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}/src/flync"


# ---------------------------------------------------------------------------
# Freshness check (same pattern as retriever/doc_retriever.py) -- parameterized
# by `path`/`commit_file`/`check_time_file` so the same mechanism covers both
# src/flync/model (is_source_stale) and src/flync/core (is_core_stale).
# ---------------------------------------------------------------------------
def _github_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_latest_commit_sha(path: str = SOURCE_PATH) -> str:
    url = (
        f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/commits"
        f"?sha={REPO_BRANCH}&path={path}&per_page=1"
    )
    resp = requests.get(url, headers=_github_headers(), timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise RuntimeError(f"No commits found for {path} — check the path")
    return data[0]["sha"]


def _get_cached_commit_sha(commit_file: str = LAST_COMMIT_FILE) -> str | None:
    if not os.path.exists(commit_file):
        return None
    with open(commit_file) as f:
        return f.read().strip() or None


def _save_commit_sha(sha: str, commit_file: str = LAST_COMMIT_FILE) -> None:
    os.makedirs(os.path.dirname(commit_file), exist_ok=True)
    with open(commit_file, "w") as f:
        f.write(sha)


def _last_check_too_recent(check_time_file: str = LAST_CHECK_TIME_FILE) -> bool:
    if not os.path.exists(check_time_file):
        return False
    with open(check_time_file) as f:
        last_check = float(f.read().strip() or 0)
    return (time.time() - last_check) / 3600 < CHECK_INTERVAL_HOURS


def _record_check_time(check_time_file: str = LAST_CHECK_TIME_FILE) -> None:
    os.makedirs(os.path.dirname(check_time_file), exist_ok=True)
    with open(check_time_file, "w") as f:
        f.write(str(time.time()))


def _is_path_stale(
    path: str, commit_file: str, check_time_file: str,
) -> tuple[bool, str | None]:
    """Returns (is_stale, latest_sha). Throttled: skips the API call
    entirely if the last check was less than CHECK_INTERVAL_HOURS ago."""
    if _last_check_too_recent(check_time_file):
        return False, _get_cached_commit_sha(commit_file)

    latest_sha = _get_latest_commit_sha(path)
    _record_check_time(check_time_file)
    return (latest_sha != _get_cached_commit_sha(commit_file)), latest_sha


def is_source_stale() -> tuple[bool, str | None]:
    """Same as before -- freshness of src/flync/model (the DOMAINS)."""
    return _is_path_stale(SOURCE_PATH, LAST_COMMIT_FILE, LAST_CHECK_TIME_FILE)


def is_core_stale() -> tuple[bool, str | None]:
    """Freshness of src/flync/core (validators/base_models/datatypes/utils),
    checked independently since it can change without model/ changing."""
    return _is_path_stale(CORE_PATH, CORE_LAST_COMMIT_FILE, CORE_LAST_CHECK_TIME_FILE)


# ---------------------------------------------------------------------------
# Tree-API-based download (only called when stale)
# ---------------------------------------------------------------------------
# Used to parse only __init__.py's own imports (AST) and download just
# those files -- missed anything imported only TRANSITIVELY by another file
# in the same domain (ex: flync_4_ecu/controller.py imports
# can_interface.py directly, but __init__.py never imports can_interface
# itself -- can_interface.py was therefore never downloaded, even though
# Controller() genuinely needs it to import at all). Downloading the whole
# domain folder via the Tree API (same approach as download_core_package())
# sidesteps needing to trace the import graph at all -- there's no file
# left to miss.
def download_domain(domain: str, tree: list[dict]) -> list[str]:
    domain_prefix = f"{SOURCE_PATH}/{domain}/"
    domain_paths = [
        entry["path"] for entry in tree
        if entry.get("type") == "blob" and entry["path"].startswith(domain_prefix)
    ]
    written = []
    for repo_path in domain_paths:
        rel_path = repo_path[len(domain_prefix):]  # ex: "controller.py"
        local_path = f"{OUTPUT_DIR}/{domain}/{rel_path}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        resp = requests.get(f"{RAW_BASE}/{domain}/{rel_path}", timeout=15)
        if resp.status_code != 200:
            print(f"  [!] {domain}/{rel_path} introuvable (status {resp.status_code}), ignore")
            continue
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(resp.text)
        written.append(local_path)

    return written


def refresh_source_if_needed() -> bool:
    """Point d'entree principal. Retourne True si un telechargement a eu
    lieu, False si le cache local a ete reutilise tel quel."""
    stale, latest_sha = is_source_stale()

    if not stale:
        print(f"[download_source] Code source a jour (commit {str(latest_sha)[:7]}) — cache reutilise.")
        return False

    print(f"[download_source] Code source modifie (commit {latest_sha[:7]}) — telechargement...")
    tree = _list_repo_tree()  # un seul appel, reutilise pour les 11 domaines
    total_files = 0
    for domain in DOMAINS:
        files = download_domain(domain, tree)
        print(f"  {domain}: {len(files)} fichiers")
        total_files += len(files)

    _save_commit_sha(latest_sha)
    print(f"[download_source] Termine : {total_files} fichiers telecharges, nouveau commit sauvegarde.")
    return True


# ---------------------------------------------------------------------------
# flync/core/** -- pas decouvert par discover_submodule_files (qui ne suit
# que les imports internes a un domaine) car les classes du model importent
# flync.core.* comme un PACKAGE SEPARE. Necessaire uniquement pour phase2 qui
# doit reellement EXECUTER les scripts generes (phase1 ne fait qu'analyser
# le texte des docs/du model, jamais l'importer) -- voir
# phase2/.../agent_lecteur_analyste.py::_sync_repo().
# ---------------------------------------------------------------------------
def _list_repo_tree() -> list[dict]:
    """Arbre complet et recursif des fichiers du repo a REPO_BRANCH, en un
    seul appel (Git Trees API) -- plus simple/robuste que de lister chaque
    sous-dossier de core/ un par un, et reste a jour si sa structure change
    en amont (nouveau sous-package, fichier renomme, etc.)."""
    url = f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{REPO_BRANCH}?recursive=1"
    resp = requests.get(url, headers=_github_headers(), timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if data.get("truncated"):
        print("[download_source] AVERTISSEMENT: arbre de fichiers tronque par l'API GitHub "
              "(repo tres volumineux) -- certains fichiers de core/ pourraient manquer.")
    return data.get("tree", [])


def download_core_package() -> list[str]:
    """Telecharge flync/core/** + flync/__init__.py + flync/py.typed dans
    CORE_OUTPUT_DIR, en preservant la structure de sous-packages (core/validators/,
    core/datatypes/, core/base_models/, core/utils/, core/utils/multicast/,
    core/version_migrators/, core/annotations/)."""
    tree = _list_repo_tree()
    core_paths = [
        entry["path"] for entry in tree
        if entry.get("type") == "blob" and (
            entry["path"].startswith(f"{CORE_PATH}/")
            or entry["path"] in ("src/flync/__init__.py", "src/flync/py.typed")
        )
    ]
    written = []
    for repo_path in core_paths:
        rel_path = repo_path[len("src/flync/"):]  # ex: "core/validators/address.py"
        local_path = f"{CORE_OUTPUT_DIR}/{rel_path}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        resp = requests.get(f"{RAW_ROOT_BASE}/{rel_path}", timeout=15)
        if resp.status_code != 200:
            print(f"  [!] {rel_path} introuvable (status {resp.status_code}), ignore")
            continue
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(resp.text)
        written.append(local_path)
    return written


def refresh_core_if_needed() -> bool:
    """Meme mecanisme de fraicheur que refresh_source_if_needed(), pour
    flync/core/**. Retourne True si un telechargement a eu lieu."""
    stale, latest_sha = is_core_stale()

    if not stale:
        print(f"[download_source] flync/core a jour (commit {str(latest_sha)[:7]}) — cache reutilise.")
        return False

    print(f"[download_source] flync/core modifie (commit {latest_sha[:7]}) — telechargement...")
    files = download_core_package()
    _save_commit_sha(latest_sha, CORE_LAST_COMMIT_FILE)
    print(f"[download_source] Termine : {len(files)} fichiers de flync/core telecharges.")
    return True


if __name__ == "__main__":
    refresh_source_if_needed()
    refresh_core_if_needed()
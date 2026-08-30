"""
Parser FLYNC — Etape 1: telechargement du vrai code source, avec le meme
mecanisme de fraicheur que pour la doc (retriever/doc_retriever.py) :
  1. Compare le dernier commit GitHub touchant src/flync/model/ au commit
     stocke localement
  2. Ne re-telecharge que si ca a change (throttle : ne verifie meme pas
     si le dernier check date de moins de CHECK_INTERVAL_HOURS)
  3. Utilise `ast` pour decouvrir les vrais noms de fichiers par domaine
     (gere les deux styles d'import du repo : relatif et absolu)
"""
import ast
import os
import time
import requests

DOMAINS = [
    "flync_4_app", "flync_4_bus", "flync_4_communication", "flync_4_ecu",
    "flync_4_metadata", "flync_4_nm", "flync_4_safety", "flync_4_security",
    "flync_4_signal", "flync_4_someip", "flync_4_topology", "flync_4_tsn",
]

REPO_OWNER = "Technica-Engineering"
REPO_NAME = "FLYNC"
REPO_BRANCH = "main"
SOURCE_PATH = "src/flync/model"

OUTPUT_DIR = "data/flync_source"
LAST_COMMIT_FILE = f"{OUTPUT_DIR}/.last_commit"
LAST_CHECK_TIME_FILE = LAST_COMMIT_FILE + ".checked_at"
CHECK_INTERVAL_HOURS = 6

GITHUB_API_BASE = "https://api.github.com"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}/{SOURCE_PATH}"


# ---------------------------------------------------------------------------
# Freshness check (same pattern as retriever/doc_retriever.py)
# ---------------------------------------------------------------------------
def _github_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_latest_commit_sha() -> str:
    url = (
        f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/commits"
        f"?sha={REPO_BRANCH}&path={SOURCE_PATH}&per_page=1"
    )
    resp = requests.get(url, headers=_github_headers(), timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise RuntimeError(f"No commits found for {SOURCE_PATH} — check SOURCE_PATH")
    return data[0]["sha"]


def _get_cached_commit_sha() -> str | None:
    if not os.path.exists(LAST_COMMIT_FILE):
        return None
    with open(LAST_COMMIT_FILE) as f:
        return f.read().strip() or None


def _save_commit_sha(sha: str) -> None:
    os.makedirs(os.path.dirname(LAST_COMMIT_FILE), exist_ok=True)
    with open(LAST_COMMIT_FILE, "w") as f:
        f.write(sha)


def _last_check_too_recent() -> bool:
    if not os.path.exists(LAST_CHECK_TIME_FILE):
        return False
    with open(LAST_CHECK_TIME_FILE) as f:
        last_check = float(f.read().strip() or 0)
    return (time.time() - last_check) / 3600 < CHECK_INTERVAL_HOURS


def _record_check_time() -> None:
    os.makedirs(os.path.dirname(LAST_CHECK_TIME_FILE), exist_ok=True)
    with open(LAST_CHECK_TIME_FILE, "w") as f:
        f.write(str(time.time()))


def is_source_stale() -> tuple[bool, str | None]:
    """Returns (is_stale, latest_sha). Throttled: skips the API call
    entirely if the last check was less than CHECK_INTERVAL_HOURS ago."""
    if _last_check_too_recent():
        return False, _get_cached_commit_sha()

    latest_sha = _get_latest_commit_sha()
    _record_check_time()
    return (latest_sha != _get_cached_commit_sha()), latest_sha


# ---------------------------------------------------------------------------
# ast-based discovery + download (only called when stale)
# ---------------------------------------------------------------------------
def discover_submodule_files(init_py_content: str, domain: str) -> list[str]:
    """Parses one domain's __init__.py with ast, returns the list of
    submodule filenames it imports from. Handles BOTH import styles found
    across the FLYNC codebase:
      - relative:  "from .controller import X"       (level=1, module="controller")
      - absolute:  "from flync.model.flync_4_signal.forwarder import X"
                    (level=0, module="flync.model.flync_4_signal.forwarder")
    """
    tree = ast.parse(init_py_content)
    filenames = set()
    absolute_prefix = f"flync.model.{domain}."

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        if node.level == 1:
            filenames.add(node.module)
        elif node.level == 0 and node.module.startswith(absolute_prefix):
            filenames.add(node.module[len(absolute_prefix):])

    return sorted(filenames)


def download_domain(domain: str) -> list[str]:
    os.makedirs(f"{OUTPUT_DIR}/{domain}", exist_ok=True)

    init_url = f"{RAW_BASE}/{domain}/__init__.py"
    init_content = requests.get(init_url, timeout=15).text
    init_path = f"{OUTPUT_DIR}/{domain}/__init__.py"
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(init_content)

    written = [init_path]
    for name in discover_submodule_files(init_content, domain):
        url = f"{RAW_BASE}/{domain}/{name}.py"
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"  [!] {domain}/{name}.py introuvable (status {resp.status_code}), ignore")
            continue
        local_path = f"{OUTPUT_DIR}/{domain}/{name}.py"
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
    total_files = 0
    for domain in DOMAINS:
        files = download_domain(domain)
        print(f"  {domain}: {len(files)} fichiers")
        total_files += len(files)

    _save_commit_sha(latest_sha)
    print(f"[download_source] Termine : {total_files} fichiers telecharges, nouveau commit sauvegarde.")
    return True


if __name__ == "__main__":
    refresh_source_if_needed()
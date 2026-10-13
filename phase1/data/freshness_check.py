"""
Step 1 — Freshness check.

Before doing any (slow) scraping/chunking/embedding, we ask GitHub for the
latest commit SHA touching the docs folder, and compare it with what we
have cached locally. If nothing changed, we skip straight to reusing the
existing local docs + vector index.

To avoid hitting the GitHub API on every single run (e.g. if you run
main.py several times in the same hour without needing fresh docs), a
check is only performed if more than CHECK_INTERVAL_HOURS has passed
since the last check. Within that window, the local cache is trusted
with zero network calls.
"""
import os
import time
import json
import requests

from phase1.data.repo_config import (
    REPO_OWNER, REPO_NAME, REPO_BRANCH, DOCS_SOURCE_PATH,
    LAST_COMMIT_FILE, GITHUB_API_BASE,
)

CHECK_INTERVAL_HOURS = 6
LAST_CHECK_TIME_FILE = LAST_COMMIT_FILE + ".checked_at"


def _github_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_latest_commit_sha() -> str:
    """Latest commit SHA that touched the docs submodels folder on GitHub."""
    url = (
        f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/commits"
        f"?sha={REPO_BRANCH}&path={DOCS_SOURCE_PATH}&per_page=1"
    )
    resp = requests.get(url, headers=_github_headers(), timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise RuntimeError("No commits found for the docs path — check DOCS_SOURCE_PATH")
    return data[0]["sha"]


def get_cached_commit_sha() -> str | None:
    if not os.path.exists(LAST_COMMIT_FILE):
        return None
    with open(LAST_COMMIT_FILE) as f:
        return f.read().strip() or None


def save_commit_sha(sha: str) -> None:
    os.makedirs(os.path.dirname(LAST_COMMIT_FILE), exist_ok=True)
    with open(LAST_COMMIT_FILE, "w") as f:
        f.write(sha)


def _last_check_too_recent() -> bool:
    if not os.path.exists(LAST_CHECK_TIME_FILE):
        return False
    with open(LAST_CHECK_TIME_FILE) as f:
        last_check = float(f.read().strip() or 0)
    hours_since = (time.time() - last_check) / 3600
    return hours_since < CHECK_INTERVAL_HOURS


def _record_check_time() -> None:
    os.makedirs(os.path.dirname(LAST_CHECK_TIME_FILE), exist_ok=True)
    with open(LAST_CHECK_TIME_FILE, "w") as f:
        f.write(str(time.time()))


def is_doc_stale() -> tuple[bool, str | None]:
    """Returns (is_stale, latest_sha).
    latest_sha is None when the throttle window skipped the actual API call —
    in that case is_stale is always False (trust the local cache).
    """
    cached_sha = get_cached_commit_sha()
    if _last_check_too_recent() and cached_sha is not None:
        return False, cached_sha

    latest_sha = get_latest_commit_sha()
    _record_check_time()
    save_commit_sha(latest_sha)
    if cached_sha is None:
        return True, latest_sha
    return (latest_sha != cached_sha), latest_sha


if __name__ == "__main__":
    stale, sha = is_doc_stale()
    print(f"Latest commit touching docs: {sha}")
    print(f"Cached commit:               {get_cached_commit_sha()}")
    print(f"Docs stale (need refresh)?   {stale}")
"""
Step 2 — Download.

Fetches every .rst file under the docs submodels path directly from
GitHub's raw content CDN and writes it to the local cache folder.
Only called when freshness_check.is_doc_stale() returns True.
"""
import os
import requests

from data.repo_config import (
    REPO_OWNER, REPO_NAME, REPO_BRANCH, DOCS_SOURCE_PATH,
    LOCAL_DOCS_DIR, GITHUB_API_BASE, GITHUB_RAW_BASE,
)
from data.freshness_check import _github_headers


def list_doc_files() -> list[dict]:
    """Lists every file in the submodels docs folder via the GitHub Contents API."""
    url = f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{DOCS_SOURCE_PATH}?ref={REPO_BRANCH}"
    resp = requests.get(url, headers=_github_headers(), timeout=15)
    resp.raise_for_status()
    entries = resp.json()
    return [e for e in entries if e["type"] == "file"]


def download_docs() -> list[str]:
    """Downloads all doc files to LOCAL_DOCS_DIR. Returns list of local paths written."""
    os.makedirs(LOCAL_DOCS_DIR, exist_ok=True)
    written = []
    for entry in list_doc_files():
        raw_url = f"{GITHUB_RAW_BASE}/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}/{DOCS_SOURCE_PATH}/{entry['name']}"
        resp = requests.get(raw_url, timeout=15)
        resp.raise_for_status()
        local_path = os.path.join(LOCAL_DOCS_DIR, entry["name"])
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(resp.text)
        written.append(local_path)
    return written


if __name__ == "__main__":
    files = download_docs()
    print(f"Downloaded {len(files)} files:")
    for f in files:
        print(f"  - {f}")
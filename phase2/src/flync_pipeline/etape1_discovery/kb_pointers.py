from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def _default_cache_dir() -> str:
    return str(Path.home() / ".flync_kb_cache")


@dataclass(frozen=True)
class KBPointers:
    repo_url: str
    branch: str
    model_root_path: str
    local_cache_dir: str = field(default_factory=_default_cache_dir)


FLYNC_KB = KBPointers(
    repo_url="https://github.com/Technica-Engineering/FLYNC.git",
    branch="main",
    model_root_path="src/flync/model",
)
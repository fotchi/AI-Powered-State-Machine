"""
retriever/doc_retriever.py

Purely local. Assumes data/flync_docs/ is already up to date (refreshed
separately, before this module is used — see main.py). This file only
reads and chunks what's already on disk, and hands each agent the
chunks for its own submodel. No network calls here.
"""
import os
import re
from dataclasses import dataclass

LOCAL_DOCS_DIR = "data/flync_docs"


@dataclass
class DocChunk:
    submodel: str
    heading: str
    text: str


_CLASS_DIRECTIVE = re.compile(r"^\.\. (?:autoclass|class)::\s*(\S+)", re.MULTILINE)
_SECTION_TITLE = re.compile(r"^(.+)\n([#*=~^-]{3,})\n", re.MULTILINE)


def _chunk_rst_file(path: str) -> list[DocChunk]:
    submodel = os.path.splitext(os.path.basename(path))[0]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    boundaries = []
    for m in _CLASS_DIRECTIVE.finditer(text):
        boundaries.append((m.start(), m.group(1)))
    for m in _SECTION_TITLE.finditer(text):
        boundaries.append((m.start(), m.group(1).strip()))
    boundaries.sort(key=lambda b: b[0])

    if not boundaries:
        return [DocChunk(submodel=submodel, heading=submodel, text=text.strip())]

    chunks = []
    for i, (pos, heading) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
        chunk_text = text[pos:end].strip()
        if chunk_text:
            chunks.append(DocChunk(submodel=submodel, heading=heading, text=chunk_text))
    return chunks


def _chunk_all_docs() -> list[DocChunk]:
    if not os.path.isdir(LOCAL_DOCS_DIR):
        raise FileNotFoundError(
            f"{LOCAL_DOCS_DIR} not found — run the doc refresh step first (see main.py)."
        )
    all_chunks = []
    for fname in sorted(os.listdir(LOCAL_DOCS_DIR)):
        if fname.endswith(".rst") and fname != "flync.rst":
            all_chunks.extend(_chunk_rst_file(os.path.join(LOCAL_DOCS_DIR, fname)))
    return all_chunks


# ---------------------------------------------------------------------------
# Public API used by the agents
# ---------------------------------------------------------------------------
_chunks_cache: list[DocChunk] | None = None


def get_chunks_for_submodel(submodel_name: str) -> list[DocChunk]:
    """Returns every chunk belonging to one submodel (e.g. 'flync_4_signal').
    Chunks are computed once per process and cached in memory.
    """
    global _chunks_cache
    if _chunks_cache is None:
        _chunks_cache = _chunk_all_docs()
    return [c for c in _chunks_cache if c.submodel == submodel_name]


def get_relevant_chunks(submodel_name: str) -> str:
    """Convenience wrapper for base_agent.py: all chunk texts for a
    submodel, concatenated and ready to drop into a prompt.
    """
    chunks = get_chunks_for_submodel(submodel_name)
    return "\n\n---\n\n".join(c.text for c in chunks)


if __name__ == "__main__":
    for submodel in ["flync_4_signal", "flync_4_topology", "flync_4_ecu"]:
        chunks = get_chunks_for_submodel(submodel)
        print(f"{submodel}: {len(chunks)} chunks")
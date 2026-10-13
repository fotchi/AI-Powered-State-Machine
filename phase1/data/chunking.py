"""
Step 3 — Chunking.

FLYNC docs are Sphinx .rst files. Each documented class starts with a
".. autoclass::" or ".. class::" directive, or a section header (title
underlined with #/*/=). We split on those boundaries so each chunk stays
a coherent, self-contained unit (one class or one section) — critical
for RAG quality, since a chunk that cuts a class definition in half
would confuse the LLM.
"""
import os
import re
from dataclasses import dataclass

from phase1.data.repo_config import LOCAL_DOCS_DIR


@dataclass
class DocChunk:
    submodel: str          # e.g. "flync_4_signal"
    heading: str            # e.g. "Signal" or "class SignalDataType"
    text: str


# Matches ".. autoclass:: some.module.ClassName" or ".. class:: ..."
_CLASS_DIRECTIVE = re.compile(r"^\.\. (?:autoclass|class)::\s*(\S+)", re.MULTILINE)
# Matches a section title: a line of text followed by a line of ###/***/===
_SECTION_TITLE = re.compile(r"^(.+)\n([#*=~^-]{3,})\n", re.MULTILINE)


def chunk_rst_file(path: str) -> list[DocChunk]:
    submodel = os.path.splitext(os.path.basename(path))[0]
    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Collect boundary positions from both class directives and section titles
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


def chunk_all_docs() -> list[DocChunk]:
    all_chunks = []
    for fname in sorted(os.listdir(LOCAL_DOCS_DIR)):
        if fname.endswith(".rst") and fname != "flync.rst":
            all_chunks.extend(chunk_rst_file(os.path.join(LOCAL_DOCS_DIR, fname)))
    return all_chunks


if __name__ == "__main__":
    chunks = chunk_all_docs()
    print(f"Total chunks: {len(chunks)}\n")
    by_submodel = {}
    for c in chunks:
        by_submodel.setdefault(c.submodel, 0)
        by_submodel[c.submodel] += 1
    for submodel, count in by_submodel.items():
        print(f"  {submodel}: {count} chunks")

    print("\n--- Example chunk (flync_4_signal) ---")
    example = next(c for c in chunks if c.submodel == "flync_4_signal")
    print(f"Heading: {example.heading}")
    print(example.text[:300])
"""
Least-privilege environment for phase1/phase2 subprocesses -- per the
Technical Design Document §9: "the AI agents only receive the minimal
data required for their task."

Previously every subprocess call passed `{**os.environ}` -- the FastAPI
process's *entire* inherited environment -- into the child. That leaks
anything else sitting in os.environ (unrelated cloud credentials, other
services' API keys, whatever the shell happened to have set) into an AI
pipeline that has no business seeing it. This builds an explicit
allowlisted environment instead: only what Windows/Python needs to run a
subprocess at all, plus the specific provider keys each pipeline actually
reads (verified against phase1/agents/llm_router.py,
phase1/graph_builder/download_source.py, and
phase2/.../etape4_developpeur/{agent_developpeur,commun}.py).
"""
from __future__ import annotations

import os

# Needed for Python/subprocess to function at all on Windows (locating the
# interpreter and any tools it shells out to, DNS resolution, temp files).
_OS_BASELINE = ("PATH", "SYSTEMROOT", "SYSTEMDRIVE", "TEMP", "TMP", "USERPROFILE", "COMSPEC")

# phase1/main.py + agents/llm_router.py (Groq actor+critic, Gemini integrator)
# + graph_builder/download_source.py, data/freshness_check.py (GitHub API).
# GROQ_API_KEYS / GOOGLE_API_KEYS_INTEGRATOR are the comma-separated
# multi-key forms llm_router.py actually reads (round-robin across keys);
# the singular forms remain as its documented single-key fallback.
PHASE1_KEYS = (
    "GROQ_API_KEYS", "GROQ_API_KEY", "GROQ_CRITIC_MODEL", "GROQ_GENERATOR_MODEL",
    "GOOGLE_API_KEYS_INTEGRATOR", "GOOGLE_API_KEY_INTEGRATOR",
    "GOOGLE_API_KEY", "GEMINI_API_KEY", "GEMINI_MODEL",
    "GITHUB_TOKEN",
)

# phase2/.../etape4_developpeur (Groq/Anthropic/Gemini/Ollama script
# generation -- get_llm() in commun.py tries them in that order). Two
# distinct Groq models depending on scenario category (see commun.py's
# get_llm(category=...)): GROQ_MODEL_PHASE2_MONO for MONO_MODULE (default
# qwen/qwen3.8-27b), GROQ_MODEL_PHASE2_CROSS for CROSS_MODULE (default
# openai/gpt-oss-120b). No OpenRouter: eliminated per explicit request,
# phase2 is Groq-only (+ the ollama/anthropic/gemini manual overrides).
PHASE2_KEYS = (
    "GROQ_API_KEYS", "GROQ_API_KEY", "GROQ_MODEL_PHASE2_MONO", "GROQ_MODEL_PHASE2_CROSS",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY", "GEMINI_API_KEY",
    "OLLAMA_MODEL", "OLLAMA_NUM_CTX",
)


def minimal_env(*key_groups: tuple[str, ...], **overrides: str) -> dict[str, str]:
    """OS baseline + only the requested key groups (only vars actually set
    are copied) + explicit overrides (e.g. PYTHONPATH).

    PYTHONIOENCODING is forced to utf-8 unconditionally (not just copied if
    already set) -- on Windows, a child Python process without it defaults
    stdout/stderr to the OS ANSI codepage (cp1252), and phase1/phase2 print
    French docstrings and warning emojis (e.g. the classification report's
    "⚠️") that cp1252 can't encode. Without this, any subprocess run crashes
    with UnicodeEncodeError the moment it happens to print such a character
    -- not a phase1/phase2 bug, a subprocess environment gap on our side."""
    env: dict[str, str] = {
        key: os.environ[key] for key in _OS_BASELINE if key in os.environ
    }
    env["PYTHONIOENCODING"] = "utf-8"
    # A child's stdout is block-buffered when piped: the streamed pipeline
    # logs (Agent Pipeline screen) then arrive in big chunks minutes apart,
    # and a long phase-1 run (e.g. filling 4 gaps, ~7 min) looks frozen.
    env["PYTHONUNBUFFERED"] = "1"
    for group in key_groups:
        for key in group:
            if key in os.environ:
                env[key] = os.environ[key]
    env.update(overrides)
    return env

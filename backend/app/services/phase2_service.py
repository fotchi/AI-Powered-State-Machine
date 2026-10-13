from __future__ import annotations

import json
import os
import subprocess
import sys
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from ..subprocess_env import PHASE2_KEYS, minimal_env

ROOT = Path(__file__).resolve().parents[3]
PHASE2_OUTPUT_ROOT = ROOT / "phase2" / "generated_scripts_"

# Persists real execution results for the "existing outputs" backlog (the
# scripts read_existing_outputs() shows with no run_id) across requests --
# without this, every page load re-derives execution_success from nothing
# and shows every script as untested, even ones already run via the
# Validation Results "Run All" button or GeneratedCode's per-script Execute.
PERSISTED_RESULTS_FILE = PHASE2_OUTPUT_ROOT / "_results.json"

# Scripts under these category folders are written by agent_developpeur.py
# to document a scenario it could NOT prove/disprove by isolated execution
# (out_of_scope: no validator reproduces the fault outside a full model;
# requires_sdk/unresolved: no matched class at all) -- see agent_developpeur.py
# lines ~858-864 which already treats REQUIRES_SDK as execution_success=None
# rather than a failure. Their sys.exit(1) is a deliberate marker, not a
# real test failure, so a bulk run must not count them as "failed".
_NOT_APPLICABLE_CATEGORIES = {"out_of_scope", "requires_sdk", "unresolved"}


def _is_not_applicable(script_path: Path) -> bool:
    return script_path.parent.name.lower() in _NOT_APPLICABLE_CATEGORIES


def _load_persisted_results() -> dict[str, dict[str, Any]]:
    if not PERSISTED_RESULTS_FILE.exists():
        return {}
    try:
        return json.loads(PERSISTED_RESULTS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_persisted_results(results: dict[str, dict[str, Any]]) -> None:
    PERSISTED_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=str(PERSISTED_RESULTS_FILE.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, PERSISTED_RESULTS_FILE)
    except BaseException:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def _flync_source_root() -> Path:
    return Path.home() / ".flync_kb_cache"


def ensure_flync_source() -> Path:
    cache_dir = _flync_source_root()
    source_root = cache_dir / "src"
    if not source_root.is_dir():
        local_source = ROOT / "phase1" / "data" / "flync_source"
        local_core = ROOT / "phase1" / "data" / "flync_core"
        # local_core must have core/ (not just exist) : every model class
        # imports from flync.core.* at runtime, so without it the copy
        # below is import-broken the same way a partial git clone would be.
        if local_source.is_dir() and (local_core / "core").is_dir():
            model_root = source_root / "flync" / "model"
            model_root.mkdir(parents=True, exist_ok=True)
            (source_root / "flync" / "__init__.py").touch()
            (source_root / "flync" / "model" / "__init__.py").touch()
            for module_dir in local_source.iterdir():
                if module_dir.is_dir() and module_dir.name.startswith("flync_4_"):
                    shutil.copytree(module_dir, model_root / module_dir.name, dirs_exist_ok=True)
            shutil.copytree(local_core / "core", source_root / "flync" / "core", dirs_exist_ok=True)
        else:
            from phase2.src.flync_pipeline.etape1_discovery.kb_discovery import sync_repo
            from phase2.src.flync_pipeline.etape1_discovery.kb_pointers import FLYNC_KB
            sync_repo(FLYNC_KB, cache_dir)
    if not source_root.is_dir():
        raise FileNotFoundError(f"FLYNC source cache missing: {source_root}")
    return source_root


def _run_one_script(script_path: Path, source_root: Path) -> dict[str, Any]:
    started = time.monotonic()
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)], cwd=ROOT,
            # Just runs the generated test script (imports flync.model.*) --
            # no LLM/provider keys needed, only PYTHONPATH to find the package.
            env=minimal_env(PYTHONPATH=str(source_root)),
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        returncode, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        returncode, stdout, stderr = None, "", f"Timed out after 30s: {exc}"
    duration = round(time.monotonic() - started, 3)

    not_applicable = _is_not_applicable(script_path)
    execution_success = None if not_applicable else (returncode == 0)
    return {
        "id": script_path.stem, "name": script_path.name, "path": str(script_path),
        "execution_success": execution_success, "skipped": not_applicable,
        "returncode": returncode, "stdout": stdout, "stderr": stderr,
        "duration_seconds": duration,
    }


def _find_script_by_id(script_id: str) -> Path:
    """Looks in the persistent backlog first, then falls back to any live
    run's own output dir -- GeneratedCode.tsx now shows a run's own scripts
    (via ?run_id=) right after generation, and its per-script Execute
    button calls back in with just the id, so this endpoint has to be able
    to find those too, not only the historical backlog."""
    matches = [path for path in PHASE2_OUTPUT_ROOT.rglob("*.py") if path.stem == script_id]
    if matches:
        return matches[0].resolve()

    runtime_root = ROOT / "backend" / "runtime"
    if runtime_root.is_dir():
        matches = [path for path in runtime_root.glob("*/generated_scripts/**/*.py") if path.stem == script_id]
        if matches:
            return max(matches, key=lambda p: p.stat().st_mtime).resolve()

    raise FileNotFoundError(f"Generated script not found: {script_id}")


def execute_existing_script(script_id: str) -> dict[str, Any]:
    script_path = _find_script_by_id(script_id)
    source_root = ensure_flync_source()
    outcome = _run_one_script(script_path, source_root)

    persisted = _load_persisted_results()
    persisted[script_path.stem] = outcome
    _save_persisted_results(persisted)
    return outcome


def execute_all_scripts() -> dict[str, Any]:
    """Runs every script in the existing-outputs backlog for real and
    persists the results, so read_existing_outputs()/Validation Results
    stop showing an eternal 0%/Pending for scripts nobody has run yet."""
    source_root = ensure_flync_source()
    persisted = _load_persisted_results()
    started = time.monotonic()

    success = failed = skipped = 0
    total = 0
    for i, path in enumerate(PHASE2_OUTPUT_ROOT.rglob("*.py")):
        total += 1
        outcome = _run_one_script(path, source_root)
        persisted[path.stem] = outcome
        if outcome["skipped"]:
            skipped += 1
        elif outcome["execution_success"]:
            success += 1
        else:
            failed += 1
        if (i + 1) % 10 == 0:
            _save_persisted_results(persisted)  # incremental checkpoint

    _save_persisted_results(persisted)
    return {
        "total": total, "success": success, "failed": failed, "skipped": skipped,
        "duration_seconds": round(time.monotonic() - started, 1),
    }


def read_existing_outputs() -> list[dict[str, Any]]:
    persisted = _load_persisted_results()
    scripts = []
    # Newest first, so what a pipeline run just added shows up at the top.
    for path in sorted(PHASE2_OUTPUT_ROOT.rglob("*.py"), key=lambda p: p.stat().st_mtime, reverse=True):
        script_type = "negative" if "_neg_" in path.name or "_negative" in path.name else "positive"
        outcome = persisted.get(path.stem)
        execution_success = outcome["execution_success"] if outcome else None
        skipped = bool(outcome["skipped"]) if outcome else False
        error = (outcome.get("stderr") or None) if outcome and execution_success is False else None
        scripts.append({
            "id": path.stem, "name": path.name, "path": str(path),
            "content": path.read_text(encoding="utf-8"),
            "type": script_type, "execution_success": execution_success,
            "skipped": skipped, "error": error,
            "duration_seconds": outcome.get("duration_seconds") if outcome else None,
        })
    return scripts


def _merge_run_into_backlog(run_scripts: list[dict[str, Any]]) -> None:
    """A finished run's scripts live under backend/runtime/<run_id>/, which
    the screens' default (no run_id) listing never reads -- so Generated
    Code / Validation Results / Dashboard would not show them next to the
    existing ones. Copy them into the backlog (same category folder) and
    record the execution result already obtained during generation, so a run
    ADDS to the lists instead of being a separate, invisible set."""
    persisted = _load_persisted_results()
    for script in run_scripts:
        source = Path(script["path"])
        dest = PHASE2_OUTPUT_ROOT / source.parent.name / source.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)  # copyfile (not copy2): fresh mtime => "newest"
        persisted[script["id"]] = {
            "id": script["id"], "name": source.name, "path": str(dest),
            "execution_success": script["execution_success"], "skipped": script["skipped"],
            "returncode": None, "stdout": "", "stderr": "", "duration_seconds": None,
        }
    _save_persisted_results(persisted)


def run_phase2(run_id: str, scenarios: list[dict[str, Any]], logs: list[str], on_log=None) -> list[dict[str, Any]]:
    runtime = ROOT / "backend" / "runtime" / run_id
    runtime.mkdir(parents=True, exist_ok=True)
    input_path = runtime / "scenarios.json"
    input_path.write_text(json.dumps({"scenarios": scenarios}, indent=2, ensure_ascii=False), encoding="utf-8")
    output_dir = runtime / "generated_scripts"
    process = subprocess.Popen(
        [sys.executable, "-m", "phase2.src.flync_pipeline.etape4_developpeur.agent_developpeur",
         "--scenarios", str(input_path), "--mode", "llm", "--llm-backend", "groq",
         "--output-dir", str(output_dir)],
        cwd=ROOT, env=minimal_env(PHASE2_KEYS, PYTHONPATH=str(ROOT)),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace",
    )
    assert process.stdout is not None
    for line in process.stdout:
        message = f"[Script Agent] {line.rstrip()}"
        logs.append(message)
        if on_log:
            on_log(message)
    code = process.wait()
    if code not in (0, 2):
        raise RuntimeError(f"Script Agent failed with exit code {code}")

    return collect_run_scripts(output_dir, code)


def collect_run_scripts(output_dir: Path, exit_code: int) -> list[dict[str, Any]]:
    """Builds the script list of a finished run from its output dir (and
    merges it into the backlog)."""
    # Per-script results written by agent_developpeur.py's main() --
    # without this, the only signal available here was the BATCH exit
    # code, which is non-zero the moment ONE scenario out of many fails,
    # wrongly marking every other (successfully executed) script in the
    # same run as failed too. Falls back to the old exit-code-wide guess
    # if the file is missing (e.g. an older agent_developpeur.py).
    results_file = output_dir / "_results.json"
    per_script_results: dict[str, bool | None] = {}
    if results_file.exists():
        per_script_results = json.loads(results_file.read_text(encoding="utf-8"))

    scripts = []
    for path in output_dir.rglob("*.py"):
        script_type = "negative" if "_neg_" in path.name or "_negative" in path.name else "positive"
        not_applicable = _is_not_applicable(path)
        if path.stem in per_script_results:
            execution_success = per_script_results[path.stem]
        else:
            execution_success = None if not_applicable else exit_code == 0
        scripts.append({
            "id": path.stem, "name": path.name, "path": str(path),
            "content": path.read_text(encoding="utf-8"),
            "type": script_type,
            "execution_success": execution_success,
            "skipped": not_applicable,
            "error": None,
        })
    _merge_run_into_backlog(scripts)
    return scripts

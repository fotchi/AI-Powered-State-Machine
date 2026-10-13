from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from ..subprocess_env import PHASE1_KEYS, minimal_env

ROOT = Path(__file__).resolve().parents[3]
PHASE1_ROOT = ROOT / "phase1"

# Doit matcher phase1/single_run.py::AGENTS_BY_KEY -- dupliqué ici pour ne
# pas dépendre des libs lourdes de phase1 (langgraph, sentence-transformers...)
# depuis le process backend.
KNOWN_MODULES = {
    "app", "bus", "communication", "ecu", "metadata", "nm",
    "security", "signal", "someip", "topology", "tsn",
}


def read_existing_outputs() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for filename in ("scenarios_submodels.json", "scenarios_cross_module.json"):
        path = PHASE1_ROOT / "output" / filename
        if not path.exists():
            continue
        items = json.loads(path.read_text(encoding="utf-8")).get("scenarios", [])
        # New scenarios are appended to scenarios_submodels.json: reverse it so
        # the most recent come first (Dashboard "Recent Scenarios", lists).
        scenarios.extend(reversed(items) if filename == "scenarios_submodels.json" else items)
    return scenarios


def _stream_subprocess(args: list[str], logs: list[str], on_log=None) -> None:
    process = subprocess.Popen(
        args, cwd=PHASE1_ROOT,
        env=minimal_env(PHASE1_KEYS, PYTHONPATH=str(ROOT)),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace",
    )
    assert process.stdout is not None
    for line in process.stdout:
        message = f"[Scenario Agent] {line.rstrip()}"
        logs.append(message)
        if on_log:
            on_log(message)
    code = process.wait()
    if code != 0:
        raise RuntimeError(f"Scenario Agent failed with exit code {code}")


def run_phase1(logs: list[str], on_log=None, requirements: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Si `requirements` contient un `module` reconnu (voir KNOWN_MODULES),
    ne lance QUE cet agent avec la requirement custom injectée dans le
    prompt (run_single_cli.py). Sinon, comportement inchangé : relance le
    pipeline complet (main.py -- 11 agents + cross-module)."""
    if (requirements or {}).get("mode") == "fill_coverage":
        # "Generate New Scenario" (automatic): fill the gaps of one State
        # Machine, then hand exactly those new scenarios to the Script Agent
        # (pipeline_service runs run_phase2 right after this returns).
        machine_key = str(requirements.get("machine", "")).strip().lower()
        _stream_subprocess([sys.executable, "coverage_cli.py", "fill", machine_key], logs, on_log)
        targeted_path = PHASE1_ROOT / "output" / ".last_targeted_scenarios.json"
        scenarios = json.loads(targeted_path.read_text(encoding="utf-8")) if targeted_path.exists() else []
        if not scenarios:
            raise RuntimeError(f"No new scenario was generated for State Machine '{machine_key}'")
        return scenarios

    module_key = str((requirements or {}).get("module", "")).strip().lower()

    is_targeted_run = module_key in KNOWN_MODULES
    if is_targeted_run:
        _stream_subprocess(
            [sys.executable, "run_single_cli.py", json.dumps(requirements)],
            logs, on_log,
        )
        # Only the scenario(s) just generated -- NOT read_existing_outputs(),
        # which returns the entire accumulated backlog (hundreds of
        # scenarios from every past run). Feeding that whole backlog to
        # run_phase2() on every single targeted submit silently turned a
        # "generate one scenario" request into "regenerate scripts for
        # everything ever created", which could take many minutes/hours
        # and burn Groq quota for no reason.
        targeted_path = PHASE1_ROOT / "output" / ".last_targeted_scenarios.json"
        scenarios = json.loads(targeted_path.read_text(encoding="utf-8")) if targeted_path.exists() else []
    else:
        if module_key:
            logs.append(f"[Scenario Agent] Module '{module_key}' non reconnu -- relance du pipeline complet.")
        _stream_subprocess([sys.executable, "main.py"], logs, on_log)
        scenarios = read_existing_outputs()

    required_outputs = ("scenarios_submodels.json",) if is_targeted_run else ("scenarios_submodels.json", "scenarios_cross_module.json")
    missing_outputs = [filename for filename in required_outputs if not (PHASE1_ROOT / "output" / filename).exists()]
    if missing_outputs:
        raise FileNotFoundError(f"Scenario Agent output missing: {', '.join(missing_outputs)}")
    if not scenarios:
        raise RuntimeError("Scenario Agent produced no scenarios")
    return scenarios
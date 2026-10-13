"""
Wrapper CLI autour de single_run.run_single -- garde le même pattern
subprocess + stdout-streaming que main.py (voir backend/app/services/
phase1_service.py, qui lit stdout ligne par ligne pour le WebSocket).

Usage:
    python run_single_cli.py '<requirements JSON>'
"""
import json
import sys

from dotenv import load_dotenv

load_dotenv()

from phase1.single_run import run_single  # noqa: E402


TARGETED_OUTPUT_PATH = "output/.last_targeted_scenarios.json"


def main() -> None:
    if len(sys.argv) < 2:
        print("[run_single_cli] ERROR: missing requirements JSON argument", file=sys.stderr)
        sys.exit(1)

    requirements = json.loads(sys.argv[1])
    print(f"[run_single_cli] Starting targeted generation for module={requirements.get('module')!r}")
    scenarios = run_single(requirements)

    # Sidecar with ONLY the newly generated scenario(s) -- separate from the
    # full accumulated output/scenarios_submodels.json that run_single()
    # also merges into (hundreds of scenarios across every past run).
    # backend/app/services/phase1_service.py reads THIS file for a targeted
    # run so the Script Agent stage only processes what the user just
    # asked for, instead of silently re-running script generation for the
    # entire historical backlog on every single "Generate Scenario" submit.
    with open(TARGETED_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump([s.to_dict() for s in scenarios], f, indent=2, ensure_ascii=False)

    print(
        f"[run_single_cli] Done -- {len(scenarios)} scenario(s) generated and "
        f"merged into output/scenarios_submodels.json"
    )


if __name__ == "__main__":
    main()
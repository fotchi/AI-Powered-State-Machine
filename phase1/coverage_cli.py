"""
CLI pour le coverage engine -- même pattern que run_single_cli.py (argv,
pas de code Python généré dynamiquement).

Usage:
    python coverage_cli.py report <machine_key>
    python coverage_cli.py fill <machine_key>

machine_key est un des 12 objets FLYNC couverts (voir AVAILABLE_MACHINES) --
un par State Machine de la proposition d'architecture révisée (ECU,
Controller, Ethernet, CAN, LIN, Socket, Endpoint, Deployment, SOME/IP,
PDU, Signal, Frame -- Socket/Endpoint/Deployment et PDU/Signal/Frame ont
été éclatés en machines indépendantes par rapport à la V1 du document,
cf. section 15 de la proposition révisée: "develop each block as an
independent State Machine").
"""
import importlib
import json
import sys

from dotenv import load_dotenv

# "report" now makes an LLM call (semantic_matcher.judge_coverage_via_llm)
# and "fill" always has -- same pattern as run_single_cli.py/main.py:
# without this, GROQ_API_KEYS never reaches this process's os.environ at
# all (the backend's own uvicorn process never loads phase1/.env itself,
# it only forwards whatever's already in ITS os.environ -- which is
# nothing, since nothing put it there). cwd is phase1/ (see
# backend/app/routers/coverage.py's cwd=PHASE1_ROOT), so this finds
# phase1/.env with no path needed, same as every other phase1 entry point.
load_dotenv()

AVAILABLE_MACHINES = {
    "ecu": ("ecu_machine", "ECU_MACHINE"),
    "controller": ("controller_machine", "CONTROLLER_MACHINE"),
    "ethernet": ("ethernet_machine", "ETHERNET_MACHINE"),
    "can": ("can_machine", "CAN_MACHINE"),
    "lin": ("lin_machine", "LIN_MACHINE"),
    "socket": ("socket_machine", "SOCKET_MACHINE"),
    "endpoint": ("endpoint_machine", "ENDPOINT_MACHINE"),
    "deployment": ("deployment_machine", "DEPLOYMENT_MACHINE"),
    "someip": ("someip_machine", "SOMEIP_MACHINE"),
    "pdu": ("pdu_machine", "PDU_MACHINE"),
    "signal": ("signal_machine", "SIGNAL_MACHINE"),
    "frame": ("frame_machine", "FRAME_MACHINE"),
}


def _load_machine(machine_key: str) -> dict:
    module_name, attr_name = AVAILABLE_MACHINES[machine_key]
    module = importlib.import_module(f"phase1.coverage.state_machines.{module_name}")
    return getattr(module, attr_name)


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: coverage_cli.py <report|fill|list> [machine_key]"}))
        sys.exit(1)

    action = sys.argv[1]

    if action == "list":
        print(json.dumps([
            {"key": key, "phase1_module": _load_machine(key)["phase1_module"]}
            for key in AVAILABLE_MACHINES
        ]))
        return

    if action == "describe-all":
        # Full structure (states, transitions, coverage_tags) of every
        # machine in one call -- for the frontend's State Machine explorer
        # to render the real architecture instead of a mock diagram.
        print(json.dumps({key: _load_machine(key) for key in AVAILABLE_MACHINES}))
        return

    if action == "consistency":
        from phase1.coverage.consistency import check_consistency
        print(json.dumps(check_consistency()))
        return

    if len(sys.argv) < 3:
        print(json.dumps({"error": "usage: coverage_cli.py <report|fill> <machine_key>"}))
        sys.exit(1)
    machine_key = sys.argv[2]

    if machine_key not in AVAILABLE_MACHINES:
        print(json.dumps({"error": f"State Machine inconnue: '{machine_key}'. Disponibles: {sorted(AVAILABLE_MACHINES)}"}))
        sys.exit(1)

    machine = _load_machine(machine_key)

    if action == "report":
        from phase1.coverage.matcher import coverage_report
        result = coverage_report(machine)
    elif action == "fill":
        from phase1.coverage.gap_filler import fill_coverage_gaps
        result = fill_coverage_gaps(machine)
        # Only the scenarios THIS fill just generated, same sidecar
        # run_single_cli.py writes -- lets the backend feed exactly these
        # (not the whole accumulated backlog) to the Script Agent.
        new_scenarios = result.pop("scenarios", [])
        with open("output/.last_targeted_scenarios.json", "w", encoding="utf-8") as f:
            json.dump(new_scenarios, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps({"error": f"action inconnue: {action}"}))
        sys.exit(1)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
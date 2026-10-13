"""Section 11 -- Signal, extracted from the 'PDU / Signal / Frame' chain
into its own State Machine (see pdu_machine.py for context). Mappé sur
l'agent 'signal'."""

SIGNAL_MACHINE = {
    "id": "SIGNAL_MACHINE",
    "phase1_module": "signal",
    "states": {
        "CREATE_SIGNAL": {"on_pass": "VALIDATE_SIGNAL", "on_fail": "FAIL_SIGNAL"},
        "VALIDATE_SIGNAL": {"on_pass": "SIGNAL_READY", "on_fail": "FAIL_SIGNAL", "coverage_tag": "signal.validate"},
    },
    "terminal_pass": "SIGNAL_READY",
}

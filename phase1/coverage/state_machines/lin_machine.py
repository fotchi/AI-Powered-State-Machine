"""Section 8 -- LIN State Machine. Mappé sur l'agent 'bus' (même focus
déclaré que CAN, cf. commentaire dans can_machine.py)."""

LIN_MACHINE = {
    "id": "LIN_MACHINE",
    "phase1_module": "bus",
    "states": {
        "CREATE_LIN_INTERFACE": {"on_pass": "SELECT_LIN_ROLE", "on_fail": "FAIL_LIN"},
        "SELECT_LIN_ROLE": {"on_pass": "VALIDATE_LIN", "on_fail": "FAIL_LIN", "coverage_tag": "lin.role"},
        "VALIDATE_LIN": {"on_pass": "LIN_READY", "on_fail": "FAIL_LIN", "coverage_tag": "lin.validate"},
    },
    "terminal_pass": "LIN_READY",
}
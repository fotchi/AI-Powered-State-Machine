"""Section 11 -- Frame, extracted from the 'PDU / Signal / Frame' chain
into its own State Machine (see pdu_machine.py for context). Includes the
doc's explicit post-READY cross-checks ('Then: FRAME_READY ->
VALIDATE_FRAME_BUS_BINDING -> VALIDATE_PDU_DEPLOYMENT ->
CROSS_DOMAIN_VALIDATION') as additional testable states, since the doc
treats them as real validation steps, not just narrative. Mappé sur
l'agent 'signal'."""

FRAME_MACHINE = {
    "id": "FRAME_MACHINE",
    "phase1_module": "signal",
    "states": {
        "CREATE_FRAME": {"on_pass": "VALIDATE_FRAME", "on_fail": "FAIL_FRAME"},
        "VALIDATE_FRAME": {"on_pass": "FRAME_READY", "on_fail": "FAIL_FRAME", "coverage_tag": "frame.validate"},
        "FRAME_READY": {"on_pass": "VALIDATE_FRAME_BUS_BINDING", "on_fail": "FAIL_FRAME"},
        "VALIDATE_FRAME_BUS_BINDING": {
            "on_pass": "VALIDATE_PDU_DEPLOYMENT",
            "on_fail": "FAIL_BUS_BINDING",
            "coverage_tag": "frame.bus_binding",
        },
        "VALIDATE_PDU_DEPLOYMENT": {
            "on_pass": "CROSS_DOMAIN_VALIDATION",
            "on_fail": "FAIL_PDU_DEPLOYMENT",
            "coverage_tag": "frame.pdu_deployment",
        },
        "CROSS_DOMAIN_VALIDATION": {
            "on_pass": "FRAME_CROSS_DOMAIN_READY",
            "on_fail": "FAIL_CROSS_DOMAIN",
            "coverage_tag": "frame.cross_domain",
        },
    },
    "terminal_pass": "FRAME_CROSS_DOMAIN_READY",
}

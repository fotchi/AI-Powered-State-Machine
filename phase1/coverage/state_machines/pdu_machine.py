"""Section 11 -- 'PDU / Signal / Frame' split into 3 independent State
Machines per the revised architecture proposal (section 15). This file
covers PDU only. Mappé sur l'agent 'signal' (le plus proche des 11 agents
réels)."""

PDU_MACHINE = {
    "id": "PDU_MACHINE",
    "phase1_module": "signal",
    "states": {
        "CREATE_PDU": {"on_pass": "VALIDATE_PDU", "on_fail": "FAIL_PDU"},
        "VALIDATE_PDU": {"on_pass": "PDU_READY", "on_fail": "FAIL_PDU", "coverage_tag": "pdu.validate"},
    },
    "terminal_pass": "PDU_READY",
}

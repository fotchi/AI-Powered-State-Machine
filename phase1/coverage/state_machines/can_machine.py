"""Section 7 -- CAN State Machine. Mappé sur l'agent 'bus' (focus déclaré:
'CANBus, LINBus, LIN Schedule Tables')."""

CAN_MACHINE = {
    "id": "CAN_MACHINE",
    "phase1_module": "bus",
    "states": {
        "CREATE_CAN_INTERFACE": {"on_pass": "VALIDATE_CAN_FIELDS", "on_fail": "FAIL_CAN"},
        "VALIDATE_CAN_FIELDS": {"on_pass": "RESOLVE_BUS_REF", "on_fail": "FAIL_CAN", "coverage_tag": "can.fields"},
        "RESOLVE_BUS_REF": {"on_pass": "FRAME_REFS", "on_fail": "FAIL_REFERENCE", "coverage_tag": "can.bus_ref"},
        "FRAME_REFS": {"on_pass": "CAN_INTERFACE_READY", "on_fail": "FAIL_REFERENCE", "coverage_tag": "can.frame_refs"},
    },
    "terminal_pass": "CAN_INTERFACE_READY",
}
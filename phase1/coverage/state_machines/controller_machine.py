"""Section 4 de la proposition -- Controller Sub-State Machine.
Mappé sur l'agent réel 'ecu' (Controller est une dépendance de l'ECU
dans le graphe global, section 1)."""

CONTROLLER_MACHINE = {
    "id": "CONTROLLER_MACHINE",
    "phase1_module": "ecu",
    "states": {
        "CREATE_CONTROLLER": {"on_pass": "VALIDATE_CONTROLLER", "on_fail": "FAIL_CONTROLLER"},
        "VALIDATE_CONTROLLER": {"on_pass": "RESOLVE_CONTROLLER_REFS", "on_fail": "FAIL_CONTROLLER", "coverage_tag": "controller.fields"},
        "RESOLVE_CONTROLLER_REFS": {"on_pass": "DETERMINE_INTERFACES", "on_fail": "FAIL_REFERENCE", "coverage_tag": "controller.refs"},
        "DETERMINE_INTERFACES": {"on_pass": "CREATE_INTERFACE_BINDINGS", "on_fail": "FAIL_REFERENCE", "coverage_tag": "controller.interfaces"},
        "CREATE_INTERFACE_BINDINGS": {"on_pass": "VALIDATE_CONTROLLER_BINDINGS", "on_fail": "FAIL_RELATION", "coverage_tag": "controller.bindings"},
        "VALIDATE_CONTROLLER_BINDINGS": {"on_pass": "CONTROLLER_READY", "on_fail": "FAIL_RELATION", "coverage_tag": "controller.validate_bindings"},
    },
    "terminal_pass": "CONTROLLER_READY",
}
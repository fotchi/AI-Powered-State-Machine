"""Section 9 -- Endpoint, extracted from the 'Socket -> Endpoint ->
Deployment' chain into its own State Machine (see socket_machine.py for
context). Mappé sur l'agent 'communication'."""

ENDPOINT_MACHINE = {
    "id": "ENDPOINT_MACHINE",
    "phase1_module": "communication",
    "states": {
        "CREATE_ENDPOINT": {"on_pass": "VALIDATE_ENDPOINT", "on_fail": "FAIL_ENDPOINT"},
        "VALIDATE_ENDPOINT": {"on_pass": "ENDPOINT_READY", "on_fail": "FAIL_ENDPOINT", "coverage_tag": "endpoint.validate"},
    },
    "terminal_pass": "ENDPOINT_READY",
}

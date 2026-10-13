"""Section 9 -- Deployment, extracted from the 'Socket -> Endpoint ->
Deployment' chain into its own State Machine (see socket_machine.py for
context). Mappé sur l'agent 'communication'."""

DEPLOYMENT_MACHINE = {
    "id": "DEPLOYMENT_MACHINE",
    "phase1_module": "communication",
    "states": {
        "CREATE_DEPLOYMENT": {"on_pass": "VALIDATE_DEPLOYMENT", "on_fail": "FAIL_DEPLOYMENT"},
        "VALIDATE_DEPLOYMENT": {"on_pass": "DEPLOYMENT_READY", "on_fail": "FAIL_DEPLOYMENT", "coverage_tag": "deployment.validate"},
    },
    "terminal_pass": "DEPLOYMENT_READY",
}

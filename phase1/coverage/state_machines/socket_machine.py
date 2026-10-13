"""Section 9 -- 'Socket -> Endpoint -> Deployment' split into 3 independent
State Machines per the revised architecture proposal (section 15: 'I would
add a third level... develop each block as an independent State Machine').
This file covers Socket only. Mappé sur l'agent 'communication'."""

SOCKET_MACHINE = {
    "id": "SOCKET_MACHINE",
    "phase1_module": "communication",
    "states": {
        "CREATE_SOCKET": {"on_pass": "VALIDATE_SOCKET", "on_fail": "FAIL_SOCKET"},
        "VALIDATE_SOCKET": {"on_pass": "RESOLVE_SOCKET_REFS", "on_fail": "FAIL_SOCKET", "coverage_tag": "socket.validate"},
        "RESOLVE_SOCKET_REFS": {"on_pass": "SOCKET_READY", "on_fail": "FAIL_SOCKET", "coverage_tag": "socket.refs"},
    },
    "terminal_pass": "SOCKET_READY",
}

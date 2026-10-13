"""Section 6 -- Ethernet State Machine. Mappé sur l'agent 'communication'."""

ETHERNET_MACHINE = {
    "id": "ETHERNET_MACHINE",
    "phase1_module": "communication",
    "states": {
        "CREATE_ETHERNET_INTERFACE": {"on_pass": "VALIDATE_ETH_FIELDS", "on_fail": "FAIL_ETHERNET"},
        "VALIDATE_ETH_FIELDS": {"on_pass": "RESOLVE_ETH_REFS", "on_fail": "FAIL_ETH_FIELDS", "coverage_tag": "ethernet.fields"},
        "RESOLVE_ETH_REFS": {"on_pass": "CREATE_SOCKET_CONTAINER", "on_fail": "FAIL_ETH_FIELDS", "coverage_tag": "ethernet.refs"},
    },
    "terminal_pass": "CREATE_SOCKET_CONTAINER",
}
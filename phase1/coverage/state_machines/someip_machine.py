"""Section 10 -- SOME/IP. Correspondance directe : le Scenario Agent
'someip' existe déjà tel quel. Inclut les cross-checks explicites du doc
après SOMEIP_READY ('Then: SOMEIP_READY -> VALIDATE_SOCKET_BINDING ->
VALIDATE_SERVICE_DEPLOYMENT -> VALIDATE_APP_SERVICE_REF')."""

SOMEIP_MACHINE = {
    "id": "SOMEIP_MACHINE",
    "phase1_module": "someip",
    "states": {
        "CREATE_SOMEIP": {"on_pass": "VALIDATE_SOMEIP", "on_fail": "FAIL_SOMEIP"},
        "VALIDATE_SOMEIP": {"on_pass": "SELECT_ROLE", "on_fail": "FAIL_SOMEIP", "coverage_tag": "someip.validate"},
        "SELECT_ROLE": {"on_pass": "CREATE_SERVICE", "on_fail": "FAIL_SOMEIP", "coverage_tag": "someip.role"},
        "CREATE_SERVICE": {"on_pass": "VALIDATE_SERVICE", "on_fail": "FAIL_SERVICE", "coverage_tag": "someip.service"},
        "VALIDATE_SERVICE": {"on_pass": "SOMEIP_READY", "on_fail": "FAIL_SERVICE", "coverage_tag": "someip.validate_service"},
        "SOMEIP_READY": {"on_pass": "VALIDATE_SOCKET_BINDING", "on_fail": "FAIL_SOMEIP"},
        "VALIDATE_SOCKET_BINDING": {
            "on_pass": "VALIDATE_SERVICE_DEPLOYMENT",
            "on_fail": "FAIL_SOCKET_BINDING",
            "coverage_tag": "someip.socket_binding",
        },
        "VALIDATE_SERVICE_DEPLOYMENT": {
            "on_pass": "VALIDATE_APP_SERVICE_REF",
            "on_fail": "FAIL_SERVICE_DEPLOYMENT",
            "coverage_tag": "someip.service_deployment",
        },
        "VALIDATE_APP_SERVICE_REF": {
            "on_pass": "SOMEIP_CROSS_DOMAIN_READY",
            "on_fail": "FAIL_APP_SERVICE_REF",
            "coverage_tag": "someip.app_service_ref",
        },
    },
    "terminal_pass": "SOMEIP_CROSS_DOMAIN_READY",
}
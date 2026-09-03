import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

try:
    firewall_rule = FirewallRule(
        name="Test Rule",
        action="reject",
        pattern=None,
        destination_port=65536,
        source_port=80,
        destination_ip="192.168.1.1",
        source_ip="192.168.1.2"
    )
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
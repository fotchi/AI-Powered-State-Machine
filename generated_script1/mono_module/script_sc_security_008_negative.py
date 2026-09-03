import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

try:
    firewall_rule = FirewallRule(
        name="Reject multicast",
        action="reject",
        pattern={"src_ip": "192.168.1.10", "dst_ip": "239.1.2.3", "src_port": 0, "dst_port": 0, "proto": "all"}
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
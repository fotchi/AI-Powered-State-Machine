import sys
from flync.model.flync_4_security.firewall import FirewallRule

try:
    rule = FirewallRule(
        name="rule1",
        action="reject",
        pattern={"type": "ip", "value": "192.168.1.1"},
        interface_id="ethX"
    )
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
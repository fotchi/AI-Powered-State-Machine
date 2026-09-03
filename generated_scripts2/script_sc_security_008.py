import sys
from flync.model.flync_4_security.firewall import FirewallRule, FrameFilter
from pydantic import ValidationError

try:
    firewall_rule = FirewallRule(
        name="rule1",
        action="reject",
        pattern=FrameFilter(
            source_ip="192.168.1.10",
            destination_ip="239.1.2.3",
            protocol="udp"
        )
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
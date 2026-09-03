import sys
from pydantic import ValidationError
from flync.model.flync_4_security.firewall import FirewallRule

try:
    rule = FirewallRule(
        name="rule_12",
        action="ALLOW",
        pattern="frame_filter",
        port_range={"start_port": 5000, "end_port": 80}
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    sys.exit(1)
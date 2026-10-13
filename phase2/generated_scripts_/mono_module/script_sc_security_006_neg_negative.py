import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

try:
    rule = FirewallRule(
        name="rule_12",
        action="ALLOW",
        pattern="frame_filter",
        start_port=5000,
        end_port=80
    )
except ValidationError as e:
    sys.exit(0)

print("SUCCESS")
sys.exit(0)
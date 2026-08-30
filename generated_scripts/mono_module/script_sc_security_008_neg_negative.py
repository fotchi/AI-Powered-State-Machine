import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

try:
    rule = FirewallRule(
        name="rule13",
        action="ALLOW",
        pattern="some_pattern"
    )
except ValidationError as e:
    sys.exit(0)

print("SUCCESS")
sys.exit(1)
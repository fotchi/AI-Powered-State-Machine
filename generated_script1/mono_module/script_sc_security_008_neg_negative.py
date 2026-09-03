import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

try:
    rule = FirewallRule(
        rule_id=13,
        action="ALLOW",
        protocol="ICMPX",
        pattern=None
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)
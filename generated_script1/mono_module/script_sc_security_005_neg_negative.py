import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

try:
    rule = FirewallRule(
        name="rule_11",
        action="deny",
        pattern="pattern_1",
        destination_address="10.255.255.255"
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)
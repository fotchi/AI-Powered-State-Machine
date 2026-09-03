import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

try:
    rule = FirewallRule(
        rule_id=12,
        action="ALLOW",
        pattern=None,
        port_range={"start_port": 5000, "end_port": 80}
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)
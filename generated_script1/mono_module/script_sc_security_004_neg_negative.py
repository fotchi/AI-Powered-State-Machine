import sys
from pydantic import ValidationError
from flync.model.flync_4_security.firewall import FirewallRule

try:
    rule = FirewallRule(
        rule_id=10,
        action='allow',
        source_address='300.168.1.1',
        pattern=None
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)
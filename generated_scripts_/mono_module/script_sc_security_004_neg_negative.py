import sys
from pydantic import ValidationError
from flync.model.flync_4_security.firewall import FirewallRule

try:
    rule = FirewallRule(
        name="rule10",
        action="allow",
        pattern="frame_filter"
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    sys.exit(1)
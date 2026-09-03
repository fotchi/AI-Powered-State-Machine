import sys
from flync.model.flync_4_security.firewall import FirewallRule

firewall_rule = FirewallRule(
    name="rule13",
    action="accept",
    pattern={"protocol": "tcp"}
)

print("SUCCESS")
sys.exit(0)
import sys
from flync.model.flync_4_security.firewall import Firewall, FirewallRule

firewall_rule1 = FirewallRule(
    name="rule1",
    action="reject",
    pattern={"type": "IP", "value": "192.168.0.1"}
)

firewall_rule2 = FirewallRule(
    name="rule2",
    action="accept",
    pattern={"type": "PORT", "value": 8080}
)

firewall_rule3 = FirewallRule(
    name="rule3",
    action="drop",
    pattern={"type": "IP", "value": "192.168.1.1"}
)

firewall = Firewall(
    default_action='reject',
    input_rules=[firewall_rule1],
    output_rules=[firewall_rule2],
    forward_rules=[firewall_rule3]
)

print("SUCCESS")
sys.exit(0)
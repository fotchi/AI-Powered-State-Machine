import sys
from flync.model.flync_4_security.firewall import FirewallRule, FrameFilter

firewall_rule = FirewallRule(
    name="rule-1",
    action="accept",
    pattern=FrameFilter(protocol="TCP", source_ip="192.168.1.10", destination_ip="192.168.1.20"),
    destination_port=8080,
    source_port=12345
)

print("SUCCESS")
sys.exit(0)
import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

firewall_rule1 = FirewallRule(
    name="rule1",
    action="reject",
    pattern=FrameFilter(
        ip_address="192.168.1.100",
        mac_address="00:11:22:33:44:55",
        service_id=123,
        frame_id=456
    ),
    source_ip="192.168.1.100",
    destination_ip="192.168.1.200",
    source_port=80,
    destination_port=8080,
    protocol="TCP"
)

firewall_rule2 = FirewallRule(
    name="rule2",
    action="reject",
    pattern=FrameFilter(
        ip_address="192.168.1.100",  # Same as rule1
        mac_address="00:11:22:33:44:55",  # Same as rule1
        service_id=123,  # Same as rule1
        frame_id=456  # Same as rule1
    ),
    source_ip="192.168.1.100",
    destination_ip="192.168.1.200",
    source_port=80,
    destination_port=8080,
    protocol="TCP"
)

try:
    FirewallRule(
        name="rule3",
        action="reject",
        pattern=firewall_rule2.pattern,  # Same as rule2
        source_ip="192.168.1.100",
        destination_ip="192.168.1.200",
        source_port=80,
        destination_port=8080,
        protocol="TCP"
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
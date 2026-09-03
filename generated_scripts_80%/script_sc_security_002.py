import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

try:
    obj = FirewallRule(
        name="Test Rule",
        action="reject",
        pattern=FrameFilter(ip_address="192.168.1.100", port_range=(1024, 65535)),
        source_ip="192.168.1.10",
        destination_ip="192.168.1.20",
        source_port=12345,
        protocol="TCP",
        destination_port=70000
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

class FrameFilter:
    def __init__(self, ip_address, port_range):
        self.ip_address = ip_address
        self.port_range = port_range

print("SUCCESS")
sys.exit(0)
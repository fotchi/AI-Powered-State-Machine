import sys

from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_security.firewall import Firewall
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_tsn.qos import FrameFilter

can_bus = CANBus(
    name="demo_name",
    baud_rate=1,
)
firewall = Firewall(
)
firewall_rule = FirewallRule(
    name="demo_name",
    action='reject',
    pattern=FrameFilter(),
)

print("SUCCESS")
sys.exit(0)

import sys

from flync.model.flync_4_security.firewall import Firewall
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_tsn.qos import FrameFilter

firewall = Firewall(
)
firewall_rule = FirewallRule(
    name="demo_name",
    action='reject',
    pattern=FrameFilter(),
)

print("SUCCESS")
sys.exit(0)

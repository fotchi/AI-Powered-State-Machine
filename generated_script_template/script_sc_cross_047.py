import sys

from flync.model.flync_4_security.firewall import Firewall
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SDTimings
from flync.model.flync_4_tsn.qos import FrameFilter

firewall = Firewall(
)
firewall_rule = FirewallRule(
    name="demo_name",
    action='reject',
    pattern=FrameFilter(),
)
sd_config = SDConfig(
    ip_address=None,
    sd_timings=[],
)
sd_timings = SDTimings(
    profile_id="demo_profile_id",
)

print("SUCCESS")
sys.exit(0)

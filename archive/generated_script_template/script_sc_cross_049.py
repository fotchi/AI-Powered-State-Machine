import sys

from flync.model.flync_4_security.firewall import Firewall
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_tsn.timesync import PTPPort
from flync.model.flync_4_tsn.timesync import PTPTimeReceiverConfig
from flync.model.flync_4_tsn.qos import FrameFilter

firewall = Firewall(
)
firewall_rule = FirewallRule(
    name="demo_name",
    action='reject',
    pattern=FrameFilter(),
)
ptp_config = PTPConfig(
    ptp_ports=[],
)
ptp_port = PTPPort(
    domain_id=1,
    src_port_identity=1,
    sync_config=None,
)
ptp_time_receiver_config = PTPTimeReceiverConfig(
    sync_timeout=1,
    sync_followup_timeout=1,
)

print("SUCCESS")
sys.exit(0)

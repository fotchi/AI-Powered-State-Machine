import sys
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_tsn.qos import FrameFilter
frame_filter = FrameFilter(src_mac="00:11:22:33:44:55")
firewall_rule = FirewallRule(name="AllowSSH", action="accept", pattern=frame_filter)
print("SUCCESS")
sys.exit(0)
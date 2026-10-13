import sys
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_tsn.qos import FrameFilter
from flync.core.datatypes.value_range import ValueRange

rule = FirewallRule(
    name="rule_12",
    action="accept",
    pattern=FrameFilter(dst_port=ValueRange(from_value=80, to_value=443)),
)
print("SUCCESS")
sys.exit(0)

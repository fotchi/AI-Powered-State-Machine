import sys

from flync.model.flync_4_security.firewall import Firewall
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_nm.state_management import StateManagementGroup
from flync.model.flync_4_tsn.qos import FrameFilter
from flync.model.flync_4_nm.state_management import SleepTiming

firewall = Firewall(
)
firewall_rule = FirewallRule(
    name="demo_name",
    action='reject',
    pattern=FrameFilter(),
)
group_timing = GroupTiming(
    name="demo_name",
    cycle_time_ms=1,
    sleep=SleepTiming(timeout_ms=1, wait_before_sleep_ms=1),
)
state_management_group = StateManagementGroup(
    name="demo_name",
    nm_pdu="demo_nm_pdu",
    timing_profile="demo_timing_profile",
)

print("SUCCESS")
sys.exit(0)

import sys

from flync.model.flync_4_tsn.qos import FrameFilter
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker
from flync.model.flync_4_nm.state_management import StateManagementGroup
from flync.model.flync_4_tsn.qos import Stream
from flync.model.flync_4_nm.state_management import SleepTiming

frame_filter = FrameFilter(
)
group_timing = GroupTiming(
    name="demo_name",
    cycle_time_ms=1,
    sleep=SleepTiming(timeout_ms=1, wait_before_sleep_ms=1),
)
single_rate_two_color_marker = SingleRateTwoColorMarker(
    cir=1,
    cbs=1,
    eir=0,
    ebs=1,
    coupling=False,
)
state_management_group = StateManagementGroup(
    name="demo_name",
    nm_pdu="demo_nm_pdu",
    timing_profile="demo_timing_profile",
)
stream = Stream(
    name="demo_name",
    stream_identification=[],
)

print("SUCCESS")
sys.exit(0)

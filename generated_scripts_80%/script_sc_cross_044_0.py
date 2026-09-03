import sys
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker, Stream
from flync.model.flync_4_nm.state_management import StateManagementGroup

group_timing = GroupTiming(
    name="example_group",
    description=None,
    cycle_time_ms=500,
    announcement=None,
    sleep=SleepTiming(sleep_duration=100, sleep_unit='ms'),
    extensions={}
)

single_rate_two_color_marker = SingleRateTwoColorMarker(
    cir=1000,
    cbs=2000,
    eir=0,
    ebs=3000,
    coupling=False
)

stream = Stream(
    name="example_stream",
    stream_identification=[],
    drop_at_ingress=False,
    max_sdu_size=None,
    policer=single_rate_two_color_marker,
    ipv=None,
    ats=None
)

state_management_group = StateManagementGroup(
    name="example_state_management_group",
    nm_pdu="network_management_pdu",
    timing_profile="group_timing_profile",
    description=None,
    extensions={}
)

print("SUCCESS")
sys.exit(0)
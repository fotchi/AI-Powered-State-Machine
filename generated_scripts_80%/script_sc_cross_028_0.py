import sys
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_nm.state_management import StateManagementConfig
from flync.model.flync_4_nm.state_management import StateManagementGroup

state_management_group = StateManagementGroup(
    name="test_group",
    nm_pdu="nm_pdu_reference",
    timing_profile="timing_profile_reference"
)

group_timing = GroupTiming(
    name="test_timing",
    cycle_time_ms=500,
    sleep=GroupTiming.SleepTiming(
        announcement=None,
        extensions={}
    )
)

state_management_config = StateManagementConfig(
    groups=[state_management_group],
    timing_profiles=[group_timing]
)

print("SUCCESS")
sys.exit(0)
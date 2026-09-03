import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_nm.state_management import GroupTiming, StateManagementConfig, StateManagementGroup

ecu_metadata = ECUMetadata(
    type="ECU",
    author="N/A",
    compatible_flync_version=BaseVersion("1.0"),
)

group_timing = GroupTiming(
    name="GroupTimingProfile",
    cycle_time_ms=100,
    sleep=SleepTiming(),
)

state_management_config = StateManagementConfig(
    timing_profiles=[group_timing],
)

state_management_group = StateManagementGroup(
    name="StateManagementGroup",
    nm_pdu="NM-PDU-123",
    timing_profile="GroupTimingProfile",
)

print("SUCCESS")
sys.exit(0)
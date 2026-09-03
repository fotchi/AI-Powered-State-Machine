import sys

from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_nm.state_management import StateManagementConfig
from flync.model.flync_4_nm.state_management import StateManagementGroup
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_nm.state_management import SleepTiming

ecu_metadata = ECUMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
)
group_timing = GroupTiming(
    name="demo_name",
    cycle_time_ms=1,
    sleep=SleepTiming(timeout_ms=1, wait_before_sleep_ms=1),
)
state_management_config = StateManagementConfig(
)
state_management_group = StateManagementGroup(
    name="demo_name",
    nm_pdu="demo_nm_pdu",
    timing_profile="demo_timing_profile",
)

print("SUCCESS")
sys.exit(0)

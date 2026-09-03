import sys

from flync.model.flync_4_nm.state_management import AnnouncementPhaseTiming
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SDTimings
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_nm.state_management import StateManagementConfig
from flync.model.flync_4_nm.state_management import StateManagementGroup
from flync.model.flync_4_someip.service_interface import SOMEIPTimingProfile
from flync.model.flync_4_nm.state_management import SleepTiming

announcement_phase_timing = AnnouncementPhaseTiming(
    duration_ms=1,
)
group_timing = GroupTiming(
    name="demo_name",
    cycle_time_ms=1,
    sleep=SleepTiming(timeout_ms=1, wait_before_sleep_ms=1),
)
sd_config = SDConfig(
    ip_address=None,
    sd_timings=[],
)
sd_timings = SDTimings(
    profile_id="demo_profile_id",
)
someip_config = SOMEIPConfig(
    sd_config=SDConfig(ip_address=None, sd_timings=[]),
    services=[],
    someip_timings=SOMEIPTimingProfile(),
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

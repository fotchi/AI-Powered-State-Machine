import sys
from flync.model.flync_4_nm.state_management import GroupTiming, AnnouncementPhaseTiming, SleepTiming

group_timing = GroupTiming(
    name="standard",
    cycle_time_ms=500,
    announcement=AnnouncementPhaseTiming(
        duration_ms=1000,
        burst_count=5,
        burst_cycle_time_ms=20
    ),
    sleep=SleepTiming(
        timeout_ms=2000,
        wait_before_sleep_ms=1500
    )
)

print("SUCCESS")
sys.exit(0)
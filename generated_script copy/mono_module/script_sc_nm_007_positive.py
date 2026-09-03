import sys
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_nm.state_management import SleepTiming

group_timing = GroupTiming(
    name="GroupTiming",
    cycle_time_ms=1000,
    sleep=SleepTiming(timeout_ms=2000, wait_before_sleep_ms=1500)
)

print("SUCCESS")
sys.exit(0)
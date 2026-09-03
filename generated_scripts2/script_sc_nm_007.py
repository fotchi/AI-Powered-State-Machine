import sys

from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_nm.state_management import SleepTiming

group_timing = GroupTiming(
    name="demo_name",
    cycle_time_ms=1,
    sleep=SleepTiming(timeout_ms=1, wait_before_sleep_ms=1),
)
sleep_timing = SleepTiming(
    timeout_ms=1,
    wait_before_sleep_ms=1,
)

print("SUCCESS")
sys.exit(0)

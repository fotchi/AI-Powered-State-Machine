import sys
from flync.model.flync_4_nm.state_management import SleepTiming

sleep_timing = SleepTiming(timeout_ms=2000, wait_before_sleep_ms=1500)
print("SUCCESS")
sys.exit(0)
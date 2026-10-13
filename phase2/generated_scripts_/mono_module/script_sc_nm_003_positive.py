import sys
from flync.model.flync_4_nm.state_management import AnnouncementPhaseTiming

announcement_phase_timing = AnnouncementPhaseTiming(
    duration_ms=1000,
    burst_count=5,
    burst_cycle_time_ms=20
)

print("SUCCESS")
sys.exit(0)
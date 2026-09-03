import sys
from pydantic import ValidationError
from flync.model.flync_4_nm.state_management import AnnouncementPhaseTiming

try:
    announcement_phase_timing = AnnouncementPhaseTiming(
        duration_ms=1000,
        burst_cycle_time_ms=600
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    sys.exit(1)
import sys
from pydantic import ValidationError
from flync.model.flync_4_nm.state_management import GroupTiming

try:
    group_timing = GroupTiming(
        name='standard',
        cycle_time_ms=-100,
        sleep={}
    )
except ValidationError as e:
    print("Validation failed:", e)
    sys.exit(0)

sys.exit(1)
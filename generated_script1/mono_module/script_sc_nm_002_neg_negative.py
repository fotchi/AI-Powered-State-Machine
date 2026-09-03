import sys
from pydantic import ValidationError
from flync.model.flync_4_nm.state_management import GroupTiming

try:
    group_timing = GroupTiming(
        name="standard",
        cycle_time_ms=-100,
        sleep={"duration_ms": 100}
    )
except ValidationError as e:
    print("Validation failed:", e)
    sys.exit(0)
else:
    sys.exit(1)
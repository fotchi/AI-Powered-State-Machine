import sys
from flync.model.flync_4_nm.state_management import AnnouncementPhaseTiming
from pydantic import ValidationError

try:
    obj = AnnouncementPhaseTiming(duration_ms=-1, burst_count=-1)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
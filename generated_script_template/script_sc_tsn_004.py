import sys
from pydantic import ValidationError

from flync.model.flync_4_tsn.qos import ATSInstance
from flync.model.flync_4_tsn.qos import TrafficClass

try:
    ats_instance = ATSInstance(
        committed_information_rate=1,
        committed_burst_size=1,
        max_residence_time=1,
    )
    traffic_class = TrafficClass(
        name="demo_name",
        priority=1,
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

import sys
from flync.model.flync_4_tsn.qos import ATSInstance, TrafficClass
from pydantic import ValidationError

try:
    ats_instance = ATSInstance(
        committed_information_rate=1000,
        committed_burst_size=100,
        max_residence_time=10,
        traffic_class_id='TC-99'
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
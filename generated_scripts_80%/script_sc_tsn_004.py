import sys
from flync.model.flync_4_tsn.qos import ATSInstance
from pydantic import ValidationError

try:
    ats_instance1 = ATSInstance(
        id="ats1",
        committed_information_rate=100,
        committed_burst_size=200,
        max_residence_time=300
    )
    ats_instance2 = ATSInstance(
        id="ats1",  # duplicate identifier
        committed_information_rate=150,
        committed_burst_size=250,
        max_residence_time=350
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
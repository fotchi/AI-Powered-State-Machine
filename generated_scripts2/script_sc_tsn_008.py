import sys
from flync.model.flync_4_tsn.qos import Stream, TrafficClass

try:
    stream = Stream(
        name="Stream1",
        stream_identification=[],
        traffic_class_id="TC-Missing"
    )
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
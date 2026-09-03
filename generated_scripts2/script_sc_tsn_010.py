import sys
from flync.model.flync_4_tsn.qos import DoubleRateThreeColorMarker
from pydantic import ValidationError

try:
    obj1 = DoubleRateThreeColorMarker(identifier='DRTC-01', cir=100, cbs=100, eir=100, ebs=100)
    obj2 = DoubleRateThreeColorMarker(identifier='DRTC-01', cir=200, cbs=200, eir=200, ebs=200)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
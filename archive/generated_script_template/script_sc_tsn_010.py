import sys
from pydantic import ValidationError

from flync.model.flync_4_tsn.qos import DoubleRateThreeColorMarker

try:
    double_rate_three_color_marker = DoubleRateThreeColorMarker(
        cir=1,
        cbs=1,
        eir=1,
        ebs=1,
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

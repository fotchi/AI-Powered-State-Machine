import sys
from flync.model.flync_4_tsn.qos import DoubleRateThreeColorMarker, TrafficClass
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
}

try:
    obj = DoubleRateThreeColorMarker(
        type='double_rate_three_color',
        cir=1,
        cbs=2,
        eir=3,
        ebs=4,
        coupling=True,
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

sys.exit(0)
import sys
from pydantic import ValidationError

from flync.model.flync_4_signal.frame import Frame
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker
from flync.model.flync_4_tsn.qos import Stream
from flync.model.flync_4_signal.signal import SignalDataType

try:
    frame = Frame(
        name="demo_name",
        length=1,
    )
    signal = Signal(
        name="demo_name",
        bit_length=1,
        data_type=SignalDataType.UINT8,
    )
    signal_instance = SignalInstance(
        signal=Signal(name="demo_name", bit_length=1, data_type=SignalDataType.UINT8),
    )
    single_rate_two_color_marker = SingleRateTwoColorMarker(
        cir=1,
        cbs=1,
        eir=0,
        ebs=1,
        coupling=False,
    )
    stream = Stream(
        name="demo_name",
        stream_identification=[],
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

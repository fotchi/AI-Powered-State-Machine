import sys
from flync.model.flync_4_signal.frame import Frame
from flync.model.flync_4_tsn.qos import FrameFilter, SingleRateTwoColorMarker
from flync.model.flync_4_signal.signal import Signal, SignalInstance
from flync.model.flync_4_tsn.qos import Stream

class FaultyFrameFilter(FrameFilter):
    max_frame_length = 64

frame_filter = FaultyFrameFilter()

signal_instance = SignalInstance(
    signal=Signal(
        name="test",
        data_type=SignalDataType.BYTEARRAY,
        bit_length=128
    )
)

stream = Stream(
    stream_identification=[frame_filter],
    max_sdu_size=128
)

try:
    obj = Frame(
        packed_pdus=[
            SignalInstance(
                signal=signal_instance.signal,
                bit_position=0,
                endianness='LE'
            )
        ],
        frame_usage="application",
        description="test"
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
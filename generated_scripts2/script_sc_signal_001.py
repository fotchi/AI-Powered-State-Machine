import sys
from flync.model.flync_4_signal.signal import Signal, SignalDataType

signal = Signal(
    name="example_signal",
    data_type=SignalDataType.UINT8,
    bit_length=8
)

print("SUCCESS")
sys.exit(0)
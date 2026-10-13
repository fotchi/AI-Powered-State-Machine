import sys

from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalDataType

signal = Signal(
    name="demo_name",
    bit_length=1,
    data_type=SignalDataType.UINT8,
)

print("SUCCESS")
sys.exit(0)

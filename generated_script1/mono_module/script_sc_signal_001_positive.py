import sys
from flync.model.flync_4_signal.signal import Signal, SignalDataType

signal = Signal(
    name="SpeedSignal",
    data_type=SignalDataType.UINT16,
    bit_length=16,
    factor=0.1,
    unit="km/h"
)

print("SUCCESS")
sys.exit(0)
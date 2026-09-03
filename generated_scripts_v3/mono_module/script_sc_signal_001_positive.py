import sys
from flync.model.flync_4_signal.signal import Signal, SignalDataType

signal = Signal(
    name="SpeedSignal",
    description="Speed signal in km/h",
    bit_length=16,
    data_type=SignalDataType.UINT16,
    factor=0.1,
    unit="km/h"
)

print("SUCCESS")
sys.exit(0)
import sys
from flync.model.flync_4_signal.signal import Signal, SignalDataType

signal = Signal(
    name="LinearSignal",
    description="A Signal defines factor 1.0, offset -40.0, and unit 'degC'",
    bit_length=8,
    data_type=SignalDataType.UINT8,
    factor=1.0,
    offset=-40.0,
    unit="degC",
    value_encoding=None
)

print("SUCCESS")
sys.exit(0)
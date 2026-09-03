import sys
from flync.model.flync_4_signal.signal import Signal
from pydantic import ValidationError, ValueEncoding

signal = Signal(
    name="TestSignal",
    description=None,
    bit_length=8,
    data_type=SignalDataType.UINT8,
    factor=1.0,
    offset=0.0,
    lower_limit=None,
    upper_limit=None,
    unit=None,
    initial_value=None,
    value_encoding=None
)

print("SUCCESS")
sys.exit(0)
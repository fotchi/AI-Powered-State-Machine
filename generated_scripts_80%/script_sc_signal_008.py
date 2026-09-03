import sys
from flync.model.flync_4_signal.signal import Signal, SignalInstance
from pydantic import ValidationError

signal = Signal(name="test", bit_length=8, data_type=SignalDataType.UINT16)
signal_instance = SignalInstance(signal=signal, placement={"bit_offset": 5, "length": 8})

try:
    signal_instance = SignalInstance(signal=signal, placement={"bit_offset": 5, "length": 8})
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
import sys
from flync.model.flync_4_signal.signal import Signal
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'Signal Bit Length Exceeds UINT16 Capacity'
}

signal = Signal(
    name='Test Signal',
    data_type=Signal.SignalDataType.UINT16,
    bit_length=20
)

try:
    signal = Signal(
        name='Test Signal',
        data_type=Signal.SignalDataType.UINT16,
        bit_length=20
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
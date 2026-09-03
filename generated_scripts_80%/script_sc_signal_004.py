import sys
from flync.model.flync_4_signal.signal import Signal
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'Duplicate Signal Name Within a Model'
}

signal1 = Signal(name='VehicleSpeed', data_type=Signal.SignalDataType.UINT16, bit_length=8)
signal2 = Signal(name='VehicleSpeed', data_type=Signal.SignalDataType.UINT32, bit_length=16)

try:
    signal1
    signal2
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
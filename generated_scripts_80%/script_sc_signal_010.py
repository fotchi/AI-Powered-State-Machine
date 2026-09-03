import sys
from flync.model.flync_4_signal.signal import Signal
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'Value Encoding Entry Missing Required Label Field'
}

signal = Signal(
    name='test_signal',
    data_type=Signal.SignalDataType.UINT16,
    value_encoding={
        "label": None,  # missing required field
        "value": 1
    }
)

try:
    signal.validate()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
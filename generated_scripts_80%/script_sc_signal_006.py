import sys
from flync.model.flync_4_signal.signal import Signal
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'Bitmask Flags Encoding with Overlapping Masks'
}

class Signal(Signal):
    def __init__(self, name: str, description: Optional[str] = None, bit_length: int = 8,
                 data_type: SignalDataType = Signal.SignalDataType.UINT16, factor: float = 1.0,
                 offset: float = 0.0, lower_limit: Optional[float] = None, upper_limit: Optional[float] = None,
                 unit: Optional[str] = None, initial_value: Optional[float | int | bytes | str] = None,
                 value_encoding: Optional[ValueEncoding] = None):
        self.name = name
        self.description = description
        self.bit_length = bit_length
        self.data_type = data_type
        self.factor = factor
        self.offset = offset
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.unit = unit
        self.initial_value = initial_value
        self.value_encoding = value_encoding

try:
    signal = Signal(
        name="FlagA",
        description=None,
        bit_length=8,
        data_type=Signal.SignalDataType.UINT16,
        factor=1.0,
        offset=0.0,
        lower_limit=None,
        upper_limit=None,
        unit=None,
        initial_value=None,
        value_encoding={
            "type": "bitmask_flags",
            "flags": [
                {"name": "FlagA", "mask": 0x0003},
                {"name": "FlagB", "mask": 0x0002}  # Overlapping mask
            ]
        }
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

print("SUCCESS")
sys.exit(0)
import sys
from flync.model.flync_4_signal.signal import Signal
from pydantic import ValidationError

signal = Signal(
    name="my_signal",
    description=None,
    bit_length=8,
    data_type=Signal.SignalDataType.UINT8,
    factor=1.0,
    offset=0.0,
    lower_limit=None,
    upper_limit=None,
    unit=None,
    initial_value=None,
    value_encoding={
        "type": "text_table",
        "entries": [
            {"value": 0, "description": "Park"},
            {"value": 1, "description": "Reverse"},
            {"value": 2, "description": "Neutral"},
            {"value": 3, "description": "Drive"}
        ]
    }
)

print("SUCCESS")
sys.exit(0)
import sys
from flync.model.flync_4_signal.signal import Signal
from pydantic import ValidationError

signal = Signal(
    name="Signal Combining Text Table Encoding with Linear Conversion",
    data_type=Signal.SignalDataType.UINT16,
    bit_length=16,
    factor=0.1,
    offset=0,
    unit='km/h',
    value_encoding={
        "type": "text_table",
        "mapping": {
            65535: 'Signal_Not_Available'
        }
    },
)

print("SUCCESS")
sys.exit(0)
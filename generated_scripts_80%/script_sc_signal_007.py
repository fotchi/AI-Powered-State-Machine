import sys
from flync.model.flync_4_signal.signal import Signal
from pydantic import ValidationError

signal = Signal(
    name="my_signal",
    description=None,
    bit_length=8,
    data_type=Signal.SignalDataType.UINT8,
    factor=0.5,
    offset=-40.0,
    unit='degC',
    lower_limit=-40.0,
    upper_limit=215.0,
    value_encoding={
        254: 'Sensor_Error',
        255: 'Signal_Not_Available'
    }
)

print("SUCCESS")
sys.exit(0)
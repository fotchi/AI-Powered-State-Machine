import sys

from flync.model.flync_4_signal.value_encoding import BitmaskFlag
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalDataType

bitmask_flag = BitmaskFlag(
    mask=1,
    label="demo_label",
)
signal = Signal(
    name="demo_name",
    bit_length=1,
    data_type=SignalDataType.UINT8,
)

print("SUCCESS")
sys.exit(0)

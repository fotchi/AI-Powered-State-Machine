import sys

from flync.model.flync_4_signal.value_encoding import BitfieldGroup
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalDataType

bitfield_group = BitfieldGroup(
    name="demo_name",
    mask=1,
    states=[],
)
signal = Signal(
    name="demo_name",
    bit_length=1,
    data_type=SignalDataType.UINT8,
)

print("SUCCESS")
sys.exit(0)

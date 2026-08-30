import sys

from flync.model.flync_4_signal.signal import InstancePlacement
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from flync.model.flync_4_signal.signal import SignalDataType

instance_placement = InstancePlacement(
)
signal = Signal(
    name="demo_name",
    bit_length=1,
    data_type=SignalDataType.UINT8,
)
signal_instance = SignalInstance(
    signal=Signal(name="demo_name", bit_length=1, data_type=SignalDataType.UINT8),
)

print("SUCCESS")
sys.exit(0)

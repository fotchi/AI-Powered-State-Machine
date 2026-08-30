import sys
from flync.model.flync_4_signal.signal import InstancePlacement
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance

signal = Signal(
    name="example_signal",
    bit_length=8,
    data_type="uint8",
    factor=1.0,
    offset=0.0,
    unit="none",
    initial_value=0
)

instance_placement = InstancePlacement(
    bit_position=0,
    endianness="LE"  # Correction de la casse
)

signal_instance = SignalInstance(
    signal=signal,
    bit_position=0,
    endianness="LE"
)

print("SUCCESS")
sys.exit(0)
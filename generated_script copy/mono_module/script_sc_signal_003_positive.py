import sys
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from flync.model.flync_4_signal.signal import SignalDataType

signal = Signal(name="test_signal", data_type=SignalDataType.UINT16, bit_length=16)
signal_instance = SignalInstance(signal=signal, bit_position=0, endianness="BE")

print("SUCCESS")
sys.exit(0)
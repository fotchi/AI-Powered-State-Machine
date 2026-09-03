import sys
from flync.model.flync_4_signal.signal import Signal

signal = Signal(
    name="test_signal",
    data_type="uint8",
    bit_length=8,
    description="Test signal with UINT8 data type and bit length 8"
)

print("SUCCESS")
sys.exit(0)
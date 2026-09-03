import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_signal.signal import Signal, SignalInstance
from flync.model.flync_4_metadata.metadata import SystemMetadata
from pydantic import ValidationError

system_metadata = SystemMetadata(
    type="system",
    author="N/A",
    compatible_flync_version={"major": 1, "minor": 0},
    release={"major": 1, "minor": 0}
)

ecu_metadata = ECUMetadata(
    type="ECU",
    author="N/A",
    compatible_flync_version={"major": 1, "minor": 0},
    extensions=None,
    hardware=None,
    software=None
)

signal = Signal(
    name="Signal_01",
    description=None,
    bit_length=16,
    data_type="UINT16",
    factor=1.0,
    offset=0.0,
    lower_limit=None,
    upper_limit=None,
    unit=None,
    initial_value=None,
    value_encoding=None
)

signal_instance = SignalInstance(
    signal=signal,
    bit_position=None,
    update_indication_bit_position=None,
    endianness="LE"
)

try:
    print("SUCCESS")
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
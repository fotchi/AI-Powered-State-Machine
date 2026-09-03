import sys
from pydantic import ValidationError

from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from flync.model.flync_4_signal.signal import SignalDataType

try:
    flync_channel_config = FLYNCChannelConfig(
    )
    signal = Signal(
        name="demo_name",
        bit_length=1,
        data_type=SignalDataType.UINT8,
    )
    signal_instance = SignalInstance(
        signal=Signal(name="demo_name", bit_length=1, data_type=SignalDataType.UINT8),
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

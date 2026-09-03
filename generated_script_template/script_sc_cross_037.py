import sys

from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_signal.signal import SignalDataType

controller = Controller(
    name="demo_name",
    controller_metadata=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"),
)
ecu_metadata = ECUMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
)
embedded_metadata = EmbeddedMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
    target_system="demo_target_system",
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

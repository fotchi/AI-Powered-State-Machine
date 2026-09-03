import sys

from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_metadata.metadata import SystemMetadata
from flync.model.flync_4_metadata.metadata import BaseVersion

can_bus = CANBus(
    name="demo_name",
    baud_rate=1,
)
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
system_metadata = SystemMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
    release=BaseVersion(version="demo_version"),
)

print("SUCCESS")
sys.exit(0)

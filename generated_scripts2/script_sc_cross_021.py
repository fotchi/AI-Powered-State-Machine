import sys

from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_metadata.metadata import SystemMetadata
from flync.model.flync_4_metadata.metadata import BaseVersion

ecu_metadata = ECUMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
)
flync_channel_config = FLYNCChannelConfig(
)
flync_communication_config = FLYNCCommunicationConfig(
)
system_metadata = SystemMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
    release=BaseVersion(version="demo_version"),
)

print("SUCCESS")
sys.exit(0)

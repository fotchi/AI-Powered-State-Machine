import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_metadata.metadata import SystemMetadata

ecu_metadata = ECUMetadata(
    type="ecu",
    author="N/A",
    compatible_flync_version={"major": 2, "minor": 0, "patch": 0},
    extensions={"key": "value"},
)

flync_channel_config = FLYNCChannelConfig()

system_metadata = SystemMetadata(
    type="system",
    author="N/A",
    compatible_flync_version={"major": 2, "minor": 0, "patch": 0},
    release={"major": 1, "minor": 0, "patch": 0},
)

flync_communication_config = FLYNCCommunicationConfig(
    channels=flync_channel_config,
    state_management=system_metadata,
)

print("SUCCESS")
sys.exit(0)
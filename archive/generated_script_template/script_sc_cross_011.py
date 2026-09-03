import sys

from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_signal.frame import Frame

can_bus = CANBus(
    name="demo_name",
    baud_rate=1,
)
flync_channel_config = FLYNCChannelConfig(
)
flync_communication_config = FLYNCCommunicationConfig(
)
frame = Frame(
    name="demo_name",
    length=1,
)

print("SUCCESS")
sys.exit(0)

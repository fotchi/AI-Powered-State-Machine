import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
bus = CANBus(name="MainBus", baud_rate=500000)
config = FLYNCChannelConfig(can_buses=[bus])
print("SUCCESS")
sys.exit(0)
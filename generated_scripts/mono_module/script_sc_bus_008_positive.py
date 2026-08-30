import sys

from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_bus.lin_bus import LINBus

can_bus = CANBus(
    name="demo_name",
    baud_rate=9600,
)
lin_bus = LINBus(
    name="demo_name",
    lin_protocol_version=None,
    lin_language_version=None,
    baud_rate=9600,
)

print("SUCCESS")
sys.exit(0)

import sys
from flync.model.flync_4_bus.can_bus import CANBus

can_bus = CANBus(
    name="CANBus1",
    baud_rate=250000
)

print("SUCCESS")
sys.exit(0)
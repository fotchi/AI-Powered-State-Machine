import sys
from flync.model.flync_4_bus.can_bus import CANBus

can_bus = CANBus(
    name="PowertrainCAN",
    baud_rate=500000,
    frames=[]
)

print("SUCCESS")
sys.exit(0)
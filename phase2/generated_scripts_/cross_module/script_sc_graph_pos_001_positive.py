import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_signal.frame import CANFrame
bus = CANBus(name="MainBus", baud_rate=500000, frames=[CANFrame(name="EngineSpeed", length=8, can_id=0x123, id_format="standard_11bit")])
print("SUCCESS")
sys.exit(0)
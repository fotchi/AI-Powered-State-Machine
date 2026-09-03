import sys

from flync.model.flync_4_ecu.can_interface import CANFrameRef
from flync.model.flync_4_ecu.can_interface import CANInterface

can_frame_ref = CANFrameRef(
    bus_ref="demo_bus_ref",
    frame_ref=1,
)
can_interface = CANInterface(
    name="demo_name",
    bus_ref="demo_bus_ref",
)

print("SUCCESS")
sys.exit(0)

import sys
from flync.model.flync_4_ecu.can_interface import CANFrameRef
from flync.model.flync_4_ecu.can_interface import CANInterface

# Création d'un CANFrameRef valide
can_frame_ref = CANFrameRef(bus_ref="CAN1", frame_ref=123)

# Création d'un CANInterface avec un CANFrameRef valide
can_interface = CANInterface(name="ECU1", bus_ref="CAN1", sender_frames=[can_frame_ref])

print("SUCCESS")
sys.exit(0)
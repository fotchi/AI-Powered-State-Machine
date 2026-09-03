import sys
from flync.model.flync_4_ecu.can_interface import CANInterface

# Création d'un CANInterface avec un bus_ref valide
can_interface = CANInterface(
    name="CAN_IF_1",
    bus_ref="CAN_BUS_1"
)

print("SUCCESS")
sys.exit(0)
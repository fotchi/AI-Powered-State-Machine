import sys
from flync.model.flync_4_topology.bus_topology import BusAttachmentPoint, CANBusTopology

ecu_name = "ECU1"
controller_name = "Controller1"
interface_name = "CAN0"
role = "can_node"

bus_name = "CANBus1"
bus_type = "can"

bus_attachment_point = BusAttachmentPoint(
    ecu_name=ecu_name,
    controller_name=controller_name,
    interface_name=interface_name,
    role=role
)

can_bus_topology = CANBusTopology(
    bus_name=bus_name,
    bus_type=bus_type,
    attachments=[bus_attachment_point]
)

print("SUCCESS")
sys.exit(0)
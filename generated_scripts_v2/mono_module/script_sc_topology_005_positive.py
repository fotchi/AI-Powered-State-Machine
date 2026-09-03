import sys
from flync.model.flync_4_topology.bus_topology import BusAttachmentPoint

bus_attachment_point = BusAttachmentPoint(
    ecu_name="ECU_A",
    controller_name="CAN_IF_1",
    interface_name="CAN_1",
    role="can_node"
)

print("SUCCESS")
sys.exit(0)
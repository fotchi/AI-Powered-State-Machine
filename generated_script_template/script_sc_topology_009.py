import sys

from flync.model.flync_4_topology.bus_topology import BusAttachmentPoint
from flync.model.flync_4_topology.bus_topology import CANBusTopology

bus_attachment_point = BusAttachmentPoint(
    ecu_name="demo_ecu_name",
    controller_name="demo_controller_name",
    interface_name="demo_interface_name",
    role='can_node',
)
can_bus_topology = CANBusTopology(
    bus_name="demo_bus_name",
    bus_type='can',
)

print("SUCCESS")
sys.exit(0)

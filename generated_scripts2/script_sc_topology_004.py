import sys
from flync.model.flync_4_topology.bus_topology import CANBusTopology, BusAttachmentPoint

try:
    bus_attachment = BusAttachmentPoint(bus_name="example_bus", bus_type="can")
    can_bus_topology = CANBusTopology(bus_name="example_can_bus", bus_type="can", attachments=[bus_attachment])
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
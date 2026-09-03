import sys

from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_topology.bus_topology import CANBusTopology

can_bus = CANBus(
    name="demo_name",
    baud_rate=1,
)
can_bus_topology = CANBusTopology(
    bus_name="demo_bus_name",
    bus_type='can',
)

print("SUCCESS")
sys.exit(0)

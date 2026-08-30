import sys

from flync.model.flync_4_topology.bus_topology import LINBusTopology

lin_bus_topology = LINBusTopology(
    bus_name="demo_bus_name",
    bus_type='can',
)

print("SUCCESS")
sys.exit(0)

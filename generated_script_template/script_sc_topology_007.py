import sys

from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

ethernet_topology = EthernetTopology(
    connections=[],
)
external_connection = ExternalConnection(
    id="demo_id",
    ecu1_port_name="demo_ecu1_port_name",
    ecu2_port_name="demo_ecu2_port_name",
)

print("SUCCESS")
sys.exit(0)

import sys

from flync.model.flync_4_ecu.port import ECUPort
from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_topology.ethernet_topology import FLYNCTopology

ecu_port = ECUPort(
    name="demo_name",
)
ethernet_topology = EthernetTopology(
    connections=[],
)
external_connection = ExternalConnection(
    id="demo_id",
    ecu1_port_name="demo_ecu1_port_name",
    ecu2_port_name="demo_ecu2_port_name",
)
flync_topology = FLYNCTopology(
)

print("SUCCESS")
sys.exit(0)

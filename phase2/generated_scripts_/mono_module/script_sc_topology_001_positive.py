import sys
from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

ethernet_topology = EthernetTopology(
    connections=[
        ExternalConnection(
            id="conn1",
            ecu1_port_name="ETH_1",
            ecu2_port_name="ETH_1"
        )
    ]
)

print("SUCCESS")
sys.exit(0)
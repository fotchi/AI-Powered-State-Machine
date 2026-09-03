import sys
from pydantic import ValidationError
from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

try:
    topology = EthernetTopology(
        connections=[
            ExternalConnection(id="conn1", ecu1_port_name="ETH_1", ecu2_port_name="ETH_1"),
            ExternalConnection(id="conn1", ecu1_port_name="ETH_1", ecu2_port_name="ETH_1")
        ]
    )
except ValidationError as e:
    print("Validation failed:", e)
    sys.exit(1)
else:
    print("SUCCESS")
    sys.exit(0)
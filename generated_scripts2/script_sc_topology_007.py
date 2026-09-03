import sys
from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

# Create an instance of ExternalConnection
ecu_connection = ExternalConnection(
    id="ecu_connection_1",
    ecu1_port_name="ecu1_port1",
    ecu2_port_name="ecu2_port1"
)

# Create an instance of EthernetTopology and add the external connection
ethernet_topology = EthernetTopology(
    connections=[ecu_connection]
)

# Print success message
print("SUCCESS")
sys.exit(0)
import sys
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

# Création de l'ExternalConnection avec des références correctes
external_connection = ExternalConnection(
    id='conn1',
    ecu1_port_name='CAN_H',
    ecu2_port_name='CAN_H'
)

print("SUCCESS")
sys.exit(0)
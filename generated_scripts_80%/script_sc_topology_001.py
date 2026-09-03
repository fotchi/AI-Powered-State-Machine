import sys
from pydantic import BaseModel
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

class SystemTopology(BaseModel):
    external_connection: ExternalConnection

system_topology = SystemTopology(
    external_connection=ExternalConnection(
        type='ecu_port_to_ecu_port',
        id='connection-1',
        ecu1_port_name='ECU1_PORT_1',
        ecu2_port_name='ECU2_PORT_1'
    )
)

print("SUCCESS")
sys.exit(0)
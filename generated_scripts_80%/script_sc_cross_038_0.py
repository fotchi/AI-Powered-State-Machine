import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

ecu1 = ECUMetadata(
    type="ECU",
    author="N/A",
    compatible_flync_version={"major": 1, "minor": 0},
    extensions=None,
    hardware=None,
    software=None
)

ecu2 = ECUMetadata(
    type="Zone_ECU",
    author="N/A",
    compatible_flync_version={"major": 1, "minor": 0},
    extensions=None,
    hardware=None,
    software=None
)

external_connection = ExternalConnection(
    id="connection_id",
    type="ecu_port_to_ecu_port",
    ecu1_port_name=ecu1.id,
    ecu2_port_name=ecu2.id
)

print("SUCCESS")
sys.exit(0)
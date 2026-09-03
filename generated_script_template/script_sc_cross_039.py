import sys

from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_metadata.metadata import BaseVersion

ecu_metadata = ECUMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
)
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

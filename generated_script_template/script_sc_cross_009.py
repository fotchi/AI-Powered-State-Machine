import sys

from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_app.application import ServiceConsumerReference
from flync.model.flync_4_app.application import ServiceProviderReference
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata

app_bindings = AppBindings(
)
controller = Controller(
    name="demo_name",
    controller_metadata=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"),
)
ethernet_topology = EthernetTopology(
    connections=[],
)
external_connection = ExternalConnection(
    id="demo_id",
    ecu1_port_name="demo_ecu1_port_name",
    ecu2_port_name="demo_ecu2_port_name",
)
service_consumer_reference = ServiceConsumerReference(
    instance_id=1,
    major_version=1,
)
service_provider_reference = ServiceProviderReference(
    instance_id=1,
    major_version=1,
)

print("SUCCESS")
sys.exit(0)

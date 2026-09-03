import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_app.application import ServiceConsumerReference, ServiceProviderReference

app_bindings_provider = AppBindings(
    app_refs=["App_Provider"],
)

app_bindings_consumer = AppBindings(
    app_refs=["App_Consumer"],
)

external_connection = ExternalConnection(
    type="ecu_port_to_ecu_port",
    id="connection_1",
    ecu1_port_name="port_1",
    ecu2_port_name="port_2",
)

service_consumer_reference = ServiceConsumerReference(
    type="consumer",
    service_name="service_1",
    instance_id=1,
    major_version=1,
)

service_provider_reference = ServiceProviderReference(
    type="provider",
    service_name="service_2",
    instance_id=2,
    major_version=2,
)

print("SUCCESS")
sys.exit(0)
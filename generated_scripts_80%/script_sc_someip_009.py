import sys
from flync.model.flync_4_someip.deployment import Layer4Endpoint, SOMEIPServiceProvider
from flync.model.flync_4_someip.service_interface import SOMEIPServiceInterface

layer4_endpoint = Layer4Endpoint(
    protocol='UDP',
    port=30490,
)

someip_service_interface = SOMEIPServiceInterface(
    name='EngineControl',
    id=1,
    major_version=0,
    minor_version=0
)

someip_service_provider = SOMEIPServiceProvider(
    deployment_type='SOMEIP',
    service=someip_service_interface.id,
    instance_id=1,
    someip_sd_timings_profile='default',
    provided_eventgroups=None,
    multicast_config=None
)

print("SUCCESS")
sys.exit(0)
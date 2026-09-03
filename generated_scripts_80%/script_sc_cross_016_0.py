import sys
from flync.model.flync_4_someip.deployment import Layer4Endpoint
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_someip.deployment import SOMEIPServiceDeployment

sd_config = SDConfig(
    ip_address='224.0.1.100',
    port=30490,
    sd_timings=[{'profile_id': 'some_profile', 'timing': 10, 'unit': 'ms'}],
)

someip_config = SOMEIPConfig(
    version='1.0',
    sd_config=sd_config,
    services=[{'service_name': 'my_service'}],
    someip_timings={'timing_profile': 'some_timing'},
)

layer4_endpoint = Layer4Endpoint(
    protocol='UDP',
    port=12345,
)

someip_deployment = SOMEIPServiceDeployment(
    deployment_type='SOMEIP',
    service=1,
    instance_id=1,
    someip_sd_timings_profile='some_profile',
)

print("SUCCESS")
sys.exit(0)
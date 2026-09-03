import sys

from flync.model.flync_4_someip.deployment import Layer4Endpoint
from flync.model.flync_4_someip.deployment import SOMEIPServiceDeployment

layer4_endpoint = Layer4Endpoint(
    port=1,
)
someip_service_deployment = SOMEIPServiceDeployment(
    deployment_type=None,
    service=1,
    instance_id=1,
    someip_sd_timings_profile="demo_someip_sd_timings_profile",
)

print("SUCCESS")
sys.exit(0)

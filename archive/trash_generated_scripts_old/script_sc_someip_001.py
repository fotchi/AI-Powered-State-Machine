import sys
from flync.model.flync_4_someip.deployment import SOMEIPServiceConsumer

some_ip_service_consumer = SOMEIPServiceConsumer(
    deployment_type="DeploymentTypes",
    service=123,
    major_version=1,
    instance_id=456,
    someip_sd_timings_profile="SOME/IP timings profile ussed for the deployment.",
    consumed_eventgroups=["Eventgroup1", "Eventgroup2"]
)

print("SUCCESS")
sys.exit(0)
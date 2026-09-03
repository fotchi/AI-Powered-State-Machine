import sys

from flync.model.flync_4_someip.deployment import SOMEIPServiceConsumer

someip_service_consumer = SOMEIPServiceConsumer(
    deployment_type=None,
    service=None,
    instance_id=None,
    someip_sd_timings_profile="demo_someip_sd_timings_profile",
)

print("SUCCESS")
sys.exit(0)

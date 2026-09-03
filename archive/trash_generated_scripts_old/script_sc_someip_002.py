import sys
from flync.model.flync_4_someip.deployment import SOMEIPServiceConsumer
from pydantic import ValidationError

scenario = {
    "type": "Negative",
    "description": "Subscribe to a non-existent Eventgroup"
}

try:
    obj = SOMEIPServiceConsumer(
        deployment_type="DeploymentTypes",
        service=12345,
        major_version=0,
        instance_id=1,
        someip_sd_timings_profile="someip_sd_timings_profile",
        consumed_eventgroups=["non_existent_eventgroup"]
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
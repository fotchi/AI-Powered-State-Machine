import sys
from flync.model.flync_4_someip.deployment import Layer4Endpoint
from flync.model.flync_4_someip.deployment import SOMEIPServiceDeployment
from pydantic import ValidationError

try:
    obj = SOMEIPServiceDeployment(
        deployment_type=1,
        service=0x3000,
        major_version=0,
        instance_id=1,
        someip_sd_timings_profile="profile",
        endpoint_ref=Layer4Endpoint(name='ECU1_EP')
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
import sys
from flync.model.flync_4_someip.deployment import SOMEIPServiceConsumer
from flync.model.flync_4_someip.service_interface import SOMEIPServiceInterface
from pydantic import ValidationError

someip_service_interface = SOMEIPServiceInterface(
    name='NonExistentService',
    id=1,
    major_version=0,
    minor_version=0
)

try:
    someip_service_consumer = SOMEIPServiceConsumer(
        deployment_type=SOMEIPServiceConsumer.DeploymentTypes.SERVICE_CONSUMER,
        service=someip_service_interface.id,
        instance_id=1,
        someip_sd_timings_profile='someip_sd_timings_profile',
        consumed_eventgroups=None
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
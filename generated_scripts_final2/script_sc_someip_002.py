import sys
from pydantic import ValidationError

from flync.model.flync_4_someip.deployment import SOMEIPServiceConsumer

try:
    someip_service_consumer = SOMEIPServiceConsumer(
        deployment_type=None,
        service=None,
        instance_id=None,
        someip_sd_timings_profile="demo_someip_sd_timings_profile",
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

import sys
from pydantic import ValidationError
from flync.model.flync_4_someip.service_interface import SDTimings
from flync.model.flync_4_app.application import ServiceProviderReference
try:
    obj = ServiceProviderReference(service_id=1, instance_id=1, major_version=1, sd_timing_profile=SDTimings(profile_id="profile1"))
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
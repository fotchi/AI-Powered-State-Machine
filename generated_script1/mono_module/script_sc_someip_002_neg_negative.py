import sys
from pydantic import ValidationError
from flync.model.flync_4_someip.service_interface import SDTimings

try:
    sd_timings = SDTimings(
        profile_id="example_profile",
        offer_interval=1000,
        initial_offer_delay=100,
        request_interval=0
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)
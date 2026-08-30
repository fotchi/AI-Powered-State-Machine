import sys
from flync.model.flync_4_someip.service_interface import SDTimings
from pydantic import ValidationError

try:
    sd_timings = SDTimings(
        profile_id="example_profile",
        initial_delay_min=100,
        initial_delay_max=100,
        repetitions_base_delay=30,
        repetitions_max=3,
        request_response_delay_min=10,
        request_response_delay_max=10,
        offer_cyclic_delay=1000,
        offer_ttl=3000,
        find_ttl=1000,
        subscribe_ttl=3000,
        request_interval=0
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    sys.exit(1)
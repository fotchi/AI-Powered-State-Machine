import sys
from flync.model.flync_4_someip.service_interface import SDTimings

sd_timings = SDTimings(
    profile_id="SDProfile1",
    initial_delay_min=10,
    initial_delay_max=10,
    repetitions_base_delay=30,
    repetitions_max=3,
    request_response_delay_min=10,
    request_response_delay_max=10,
    offer_cyclic_delay=1000,
    offer_ttl=3000,
    find_ttl=1000,
    subscribe_ttl=3000
)

print("SUCCESS")
sys.exit(0)
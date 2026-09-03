import sys
from flync.model.flync_4_nm.state_management import GroupTiming
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SDTimings
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_nm.state_management import SleepTiming
from flync.model.flync_4_nm.state_management import StateManagementConfig
from flync.model.flync_4_nm.state_management import StateManagementGroup

group_timing = GroupTiming(
    name="example_group",
    description=None,
    cycle_time_ms=500,
    sleep=SleepTiming(timeout_ms=1000, wait_before_sleep_ms=200),
)

state_management_config = StateManagementConfig(groups=[StateManagementGroup(name="example_group", nm_pdu="example_nmpdu", timing_profile="example_timing")], timing_profiles=[group_timing])

sd_timings = SDTimings(
    profile_id="example_profile",
    initial_delay_min=10,
    initial_delay_max=10,
    repetitions_base_delay=30,
    repetitions_max=3,
    request_response_delay_min=10,
    request_response_delay_max=10,
    offer_cyclic_delay=1000,
    offer_ttl=3000,
    find_ttl=1000,
    subscribe_ttl=3000,
)

sd_config = SDConfig(
    ip_address="192.168.1.1",
    port=30490,
    sd_timings=[sd_timings],
)

someip_config = SOMEIPConfig(
    version="1.0",
    sd_config=sd_config,
    services=None,
    someip_timings={"example_key": "example_value"},
)

print("SUCCESS")
sys.exit(0)
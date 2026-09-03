import sys
from flync.model.flync_4_tsn.qos import FrameFilter
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SDTimings
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker
from flync.model.flync_4_tsn.qos import Stream
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'SOME/IP-SD Timing Profile Message Rate Exceeds TSN Ingress Stream Policer Committed Information Rate'
}

sd_timings = SDTimings(
    profile_id='some_ip_sd_profile',
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

sd_config = SDConfig(
    ip_address='239.255.255.250',
    port=30490,
    sd_timings=[sd_timings]
)

stream = Stream(
    name='some_ip_sd_stream',
    stream_identification=[
        FrameFilter(
            ethertype=[0x88E1],
            src_mac=['00:11:22:33:44:55'],
            dst_mac=['00:66:77:88:99:aa']
        )
    ],
    policer=SingleRateTwoColorMarker(
        cir=100000,
        cbs=200000
    ),
    ipv=1
)

try:
    stream = Stream(**stream.dict())
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
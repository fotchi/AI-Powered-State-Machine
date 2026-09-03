import sys

from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SDTimings
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_ecu.sockets import TCPOption
from flync.model.flync_4_someip.service_interface import SOMEIPTimingProfile

flync_communication_config = FLYNCCommunicationConfig(
)
sd_config = SDConfig(
    ip_address=None,
    sd_timings=[],
)
sd_timings = SDTimings(
    profile_id="demo_profile_id",
)
someip_config = SOMEIPConfig(
    sd_config=SDConfig(ip_address=None, sd_timings=[]),
    services=[],
    someip_timings=SOMEIPTimingProfile(),
)
tcp_option = TCPOption(
    tcp_profile_id=1,
)

print("SUCCESS")
sys.exit(0)

import sys

from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SOMEIPTimingProfile

someip_config = SOMEIPConfig(
    sd_config=SDConfig(ip_address=None, sd_timings=[]),
    services=[],
    someip_timings=SOMEIPTimingProfile(),
)

print("SUCCESS")
sys.exit(0)

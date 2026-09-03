import sys

from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_signal.frame import Frame
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SOMEIPTimingProfile

can_bus = CANBus(
    name="demo_name",
    baud_rate=1,
)
frame = Frame(
    name="demo_name",
    length=1,
)
someip_config = SOMEIPConfig(
    sd_config=SDConfig(ip_address=None, sd_timings=[]),
    services=[],
    someip_timings=SOMEIPTimingProfile(),
)

print("SUCCESS")
sys.exit(0)

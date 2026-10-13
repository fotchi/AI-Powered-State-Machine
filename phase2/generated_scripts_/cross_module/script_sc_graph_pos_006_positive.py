import sys
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_someip.service_interface import SOMEIPConfig, SDConfig, SOMEIPTimingProfile
someip = SOMEIPConfig(sd_config=SDConfig(ip_address="239.255.0.1", sd_timings=[]), services=[], someip_timings=SOMEIPTimingProfile())
comm = FLYNCCommunicationConfig(someip_config=someip)
print("SUCCESS")
sys.exit(0)
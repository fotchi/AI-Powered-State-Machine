import sys
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SDTimings
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_ecu.sockets import TCPOption

# Create a valid configuration
tcp_profile = TCPOption(tcp_profile_id=1)
tcp_profiles = [tcp_profile]

sd_timing = SDTimings(profile_id="profile1")
sd_timings = [sd_timing]

sd_config = SDConfig(ip_address="239.1.1.1", sd_timings=sd_timings)

someip_config = SOMEIPConfig(sd_config=sd_config, services=[], someip_timings={})

communication_config = FLYNCCommunicationConfig(tcp_profiles=tcp_profiles, someip_config=someip_config)

# Print the configuration to verify it is correctly set up
print(communication_config)
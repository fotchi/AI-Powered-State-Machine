import sys
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_someip.service_interface import SDConfig, SDTimings

someip_config = SOMEIPConfig(
    version='1.0',
    sd_config=SDConfig(ip_address='192.168.1.100', port=30490),
    services=[{'id': 'service1', 'meta': {'name': 'service1'}, 'interface_name': 'interface1'}],
    someip_timings=SDTimings(
        profile_id='profile1',
        initial_delay_min=10,
        initial_delay_max=10,
        repetitions_base_delay=30,
        repetitions_max=3,
        request_response_delay_min=10,
        request_response_delay_max=10
    )
)

flync_channel_config = FLYNCChannelConfig()

flync_communication_config = FLYNCCommunicationConfig(
    tcp_profiles=[{'id': 'profile1', 'name': 'profile1'}],
    someip_config=someip_config,
    channels=flync_channel_config
)

print("SUCCESS")
sys.exit(0)
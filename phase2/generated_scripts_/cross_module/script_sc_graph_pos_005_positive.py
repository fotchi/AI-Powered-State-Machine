import sys
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_ecu.sockets import TCPOption
tcp_option = TCPOption(tcp_profile_id=1)
config = FLYNCCommunicationConfig(tcp_profiles=[tcp_option])
print("SUCCESS")
sys.exit(0)
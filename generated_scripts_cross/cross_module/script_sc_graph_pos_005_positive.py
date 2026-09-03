import sys
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_ecu.sockets import TCPOption

# Create a valid TCPOption instance
tcp_option = TCPOption(tcp_profile_id=1)

# Create a valid FLYNCCommunicationConfig instance with the tcp_profiles field referencing the TCPOption instance
communication_config = FLYNCCommunicationConfig(tcp_profiles=[tcp_option])

# Print success message
print("SUCCESS")
sys.exit(0)
import sys
from flync.model.flync_4_ecu.sockets import TCPOption

tcp_profile_id = 1  # ID du profile "default_profile"
tcp_option = TCPOption(tcp_profile_id=tcp_profile_id)

print("SUCCESS")
sys.exit(0)
import sys

from flync.model.flync_4_ecu.sockets import TCPOption

tcp_option = TCPOption(
    tcp_profile_id=1,
)

print("SUCCESS")
sys.exit(0)

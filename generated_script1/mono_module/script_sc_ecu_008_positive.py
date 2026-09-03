import sys

from flync.model.flync_4_ecu.sockets import IPv4AddressEndpoint
from flync.model.flync_4_ecu.sockets import Socket
from flync.model.flync_4_ecu.socket_container import SocketContainer
from flync.model.flync_4_ecu.sockets import SocketUDP

i_pv4_address_endpoint = IPv4AddressEndpoint(
)
socket = Socket(
    name="demo_name",
    endpoint_address=None,
    port_no=1,
)
socket_container = SocketContainer(
    name="demo_name",
)
socket_udp = SocketUDP(
    name="demo_name",
    endpoint_address=None,
    port_no=1,
)

print("SUCCESS")
sys.exit(0)

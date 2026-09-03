import sys

from flync.model.flync_4_ecu.sockets import IPv4AddressEndpoint
from flync.model.flync_4_ecu.sockets import Socket

i_pv4_address_endpoint = IPv4AddressEndpoint(
)
socket = Socket(
    name="demo_name",
    endpoint_address=None,
    port_no=1,
)

print("SUCCESS")
sys.exit(0)

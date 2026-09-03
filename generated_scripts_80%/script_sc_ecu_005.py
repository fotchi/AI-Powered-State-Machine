import sys
from flync.model.flync_4_ecu.sockets import IPv4AddressEndpoint
from flync.model.flync_4_ecu.sockets import Socket

socket = Socket(
    name="test_socket",
    endpoint_address=IPv4AddressEndpoint(address="192.168.10.5", port=13400),
    port_no=13400,
)
print("SUCCESS")
sys.exit(0)
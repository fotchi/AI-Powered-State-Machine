import sys
from pydantic import ValidationError
from flync import UDPOption, Layer4Endpoint

scenario = {
    "type": "Negative",
    "description": "Invalid UDPOption with Dangling Layer4Endpoint Reference"
}

udp_option = UDPOption(
    layer4_endpoint_id="ECU1_UdpSock",  # faulty value
    protocol=Layer4Endpoint.TCP,
    port=12345
)

try:
    udp_option.validate()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
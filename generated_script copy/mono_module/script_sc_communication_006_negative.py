import sys
from flync.model.flync_4_ecu.sockets import UDPOption
from pydantic import ValidationError

try:
    obj = UDPOption(udp_cork=False, ipv6_address="2001:db8:::1")
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
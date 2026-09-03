import sys
from flync.model.flync_4_ecu.sockets import UDPOption
from pydantic import ValidationError

try:
    obj = UDPOption(max_segment_size=1500)
    print("SUCCESS")
    sys.exit(0)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
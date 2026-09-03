import sys
from flync.model.flync_4_ecu.sockets import TCPOption

try:
    obj = TCPOption(tcp_profile_id=1, ttl=256)
except ValueError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValueError but no error was raised")
    sys.exit(1)
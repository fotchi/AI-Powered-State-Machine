import sys
from flync.model.flync_4_ecu.sockets import TCPOption
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig

class FLYNCCommunicationConfigNegative(FLYNCCommunicationConfig):
    tcp_profiles = [TCPOption(tcp_profile_id=123)]

try:
    obj = FLYNCCommunicationConfigNegative()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
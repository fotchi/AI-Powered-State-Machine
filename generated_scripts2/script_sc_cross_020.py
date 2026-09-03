import sys
from pydantic import ValidationError

from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_ecu.sockets import Socket

try:
    flync_communication_config = FLYNCCommunicationConfig(
    )
    socket = Socket(
        name="demo_name",
        endpoint_address=None,
        port_no=1,
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.controller import Controller

try:
    controller = Controller(
        name="ghost_controller",
        controller_metadata={},
        ethernet_interfaces=[{"name": "eth0", "mac_address": "00:1A:2B:3C:4D:5E"}]
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
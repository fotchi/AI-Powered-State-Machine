import sys
from pydantic import ValidationError

from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_ecu.port import ECUPort

try:
    can_bus = CANBus(
        name="demo_name",
        baud_rate=1,
    )
    ecu_port = ECUPort(
        name="demo_name",
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

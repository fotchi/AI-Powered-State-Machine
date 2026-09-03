import sys
from flync.model.flync_4_bus.can_bus import CANBus
from pydantic import ValidationError

try:
    can_bus1 = CANBus(name="CAN Bus 1", baud_rate=1000000)
    can_bus2 = CANBus(name="CAN Bus 1", baud_rate=1000000)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
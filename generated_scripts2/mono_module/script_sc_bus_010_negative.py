import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_topology.bus_topology import CANBusTopology
from pydantic import ValidationError

try:
    can_bus = CANBus(
        name="CANBus1",
        baud_rate=500000,
        frames=[],
        state_memberships=[],
        bus_name="CANBus1",
        bus_type="can",
        attachments=[]
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
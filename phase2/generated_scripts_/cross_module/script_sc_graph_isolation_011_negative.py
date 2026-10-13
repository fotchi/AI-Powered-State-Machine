import sys
from pydantic import ValidationError
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_ecu.port import ECUPort
try:
    can = CANBus(name="can_bus_1", baud_rate=500000, ecu_port_ref=ECUPort(name="ecu_port_1"))
    ecu = ECUPort(name="ecu_port_1", bus_ref=can)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
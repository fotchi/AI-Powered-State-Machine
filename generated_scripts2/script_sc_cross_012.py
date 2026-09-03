import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_ecu.port import ECUPort
from pydantic import ValidationError

try:
    ecu_port = ECUPort(name="ECU1", mdi_config="BASET1")
    can_bus = CANBus(name="CANBus1", baud_rate=500000, participating_nodes=["ECU1"])
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
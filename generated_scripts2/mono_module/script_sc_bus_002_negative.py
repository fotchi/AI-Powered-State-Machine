import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_signal.pdu import PDU
from pydantic import ValidationError

try:
    pdu1 = PDU(name="PDU1", length=8)
    pdu2 = PDU(name="PDU2", length=8)

    can_bus1 = CANBus(name="CANBus1", baud_rate=500000, frames=[pdu1])
    can_bus2 = CANBus(name="CANBus1", baud_rate=500000, frames=[pdu2])

    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
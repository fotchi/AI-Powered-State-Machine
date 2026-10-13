import sys
from pydantic import ValidationError
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_someip.service_interface import SDTimings
try:
    sd = SDTimings(profile_id="sd_profile_1")
    bus = CANBus(name="CAN1", baud_rate=500000, sd_timing_ref=sd)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
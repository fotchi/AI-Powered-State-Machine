import sys
from pydantic import ValidationError
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_signal.signal import Signal, SignalDataType
try:
    sig = Signal(name='EngineSpeed', bit_length=16, data_type=SignalDataType.UINT16)
    bus = CANBus(name='EngineBus', baud_rate=500000, safety_profile_ref='E2E_Profile_Engine')
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
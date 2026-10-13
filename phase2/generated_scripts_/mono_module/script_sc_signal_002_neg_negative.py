import sys
from pydantic import ValidationError
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from flync.model.flync_4_signal.signal import SignalDataType
try:
    sig=Signal(name="TestSignal",bit_length=8,data_type=SignalDataType.UINT8)
    obj=SignalInstance(bit_position=20,endianness='LITTLE_ENDIAN',signal=sig)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
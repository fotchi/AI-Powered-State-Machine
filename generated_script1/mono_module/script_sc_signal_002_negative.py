import sys
from flync.model.flync_4_signal.signal import Signal
from pydantic import ValidationError

try:
    signal = Signal(name="test_signal", data_type="UINT16", bit_length=20)
    print("SUCCESS")
    sys.exit(0)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
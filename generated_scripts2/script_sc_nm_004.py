import sys
from flync.model.flync_4_nm.state_management import SleepTiming
from pydantic import ValidationError

try:
    obj = SleepTiming(timeout_ms=-100, wait_before_sleep_ms=1500)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
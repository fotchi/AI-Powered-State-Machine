import sys
from flync.model.flync_4_nm.state_management import SleepTiming
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'data': {
        'timeout_ms': -5,
        'wait_before_sleep_ms': 10
    }
}

try:
    obj = SleepTiming(timeout_ms=scenario['data']['timeout_ms'], wait_before_sleep_ms=scenario['data']['wait_before_sleep_ms'])
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
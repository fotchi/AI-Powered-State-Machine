import sys
from flync.model.flync_4_nm.state_management import GroupTiming
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'data': {
        'name': 'test_group_timing',
        'cycle_time_ms': -10,
        'sleep': {'duration_ms': 1000, 'unit': 'ms'}
    }
}

try:
    obj = GroupTiming(**scenario['data'])
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
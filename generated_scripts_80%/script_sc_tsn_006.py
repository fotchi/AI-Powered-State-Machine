import sys
from flync.model.flync_4_tsn.qos import HTBInstance
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'data': {
        'root_id': '1:',
        'default_class': None,
        'child_classes': [],
        'max_burst': 2000000
    }
}

try:
    obj = HTBInstance(
        root_id=scenario['data']['root_id'],
        default_class=scenario['data']['default_class'],
        child_classes=scenario['data']['child_classes'],
        max_burst=scenario['data']['max_burst']
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
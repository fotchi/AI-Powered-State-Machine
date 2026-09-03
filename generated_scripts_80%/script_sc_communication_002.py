import sys
from pydantic import ValidationError
from flync import TCPOption, TCPProfile

scenario = {
    'type': 'Negative',
    'data': {
        'tc_option': {
            'tcp_profile_name': 'default'
        },
        'tcp_profiles': [
            {'name': 'default', 'value': 1},
            {'name': 'default', 'value': 2}
        ]
    }
}

try:
    tc_option = TCPOption(tcp_profile_name='default')
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
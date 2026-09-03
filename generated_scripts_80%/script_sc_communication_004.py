import sys
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'Invalid FLYNCChannelConfig with CAN Bus Bitrate Exceeding Maximum'
}

try:
    obj = FLYNCChannelConfig(
        can_buses=[{'name': 'can_bus', 'bitrate': 5000000}]
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
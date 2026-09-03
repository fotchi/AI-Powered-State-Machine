import sys
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from pydantic import ValidationError

try:
    channel_config = FLYNCChannelConfig(
        can_buses=[{"name": "CAN1", "baud_rate": 1000}, {"name": "CAN1", "baud_rate": 1000}]
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
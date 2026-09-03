import sys
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig, CANBus

try:
    bus1 = CANBus(name="CAN1")
    bus2 = CANBus(name="CAN1")
    config = FLYNCChannelConfig(can_buses=[bus1, bus2])
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
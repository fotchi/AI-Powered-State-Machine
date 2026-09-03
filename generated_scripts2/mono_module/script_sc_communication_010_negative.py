import sys
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig, CANBus, LINBus

try:
    bus_a = CANBus(name="bus_a")
    bus_b = CANBus(name="bus_b")

    bus_a.forwarding_chain = [bus_b]
    bus_b.forwarding_chain = [bus_a]

    channel_config = FLYNCChannelConfig(can_buses=[bus_a, bus_b])
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
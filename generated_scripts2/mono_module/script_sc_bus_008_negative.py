import sys
from flync.model.flync_4_bus.lin_bus import LINBus
from flync.model.flync_4_ecu.lin_interface import LINSlaveInterface

try:
    lin_bus = LINBus(
        name="TestBus",
        lin_protocol_version="LIN2.0",
        lin_language_version="LIN2.0",
        baud_rate=500000,
        channel_name="CAN1",
        frames=[],
        bus_ref="TestBus"
    )
    lin_slave_interface = LINSlaveInterface(
        name="TestSlave",
        bus_ref="TestBus",
        lin_protocol="LIN2.0",
        configured_nad=16,
        initial_nad=16
    )
except ValueError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValueError but no error was raised")
    sys.exit(1)
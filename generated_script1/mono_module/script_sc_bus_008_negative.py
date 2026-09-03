import sys
from pydantic import ValidationError

from flync.model.flync_4_bus.lin_bus import LINBus
from flync.model.flync_4_ecu.lin_interface import LINSlaveInterface

try:
    lin_bus = LINBus(
        name="demo_name",
        lin_protocol_version=None,
        lin_language_version=None,
        baud_rate=1,
    )
    lin_slave_interface = LINSlaveInterface(
        name="demo_name",
        bus_ref="demo_bus_ref",
        lin_protocol=None,
        configured_nad=1,
        initial_nad=1,
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

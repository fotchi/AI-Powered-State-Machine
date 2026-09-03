import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_topology.ethernet_topology import FLYNCTopology
from pydantic import ValidationError

try:
    can_bus = CANBus(name='powertrain_can', baud_rate=500000)
    topology = FLYNCTopology(can_bus_topology=[can_bus])
    topology.get_can_bus_topology()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
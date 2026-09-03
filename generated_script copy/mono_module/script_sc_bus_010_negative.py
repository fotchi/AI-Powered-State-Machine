import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_topology.bus_topology import CANBusTopology

try:
    can_bus = CANBus(
        name="CAN Bus",
        baud_rate=1000000,
        fd_enabled=False,
        fd_baud_rate=None,
        frames=[],
        state_memberships=[]
    )
    can_bus_topology = CANBusTopology(
        bus_name="CAN Bus",
        bus_type="can",
        attachments=[]
    )
except FileNotFoundError:
    print("EXPECTED ERROR: FileNotFoundError")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
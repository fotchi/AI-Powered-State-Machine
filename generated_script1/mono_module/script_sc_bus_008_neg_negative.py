import sys
from pydantic import ValidationError
from flync.model.flync_4_bus.lin_bus import LINBus
from flync.model.flync_4_ecu.lin_interface import LINMasterInterface

try:
    bus = LINBus(
        name="Bus1",
        lin_protocol_version="LIN2.0",
        lin_language_version="LIN2.0",
        baud_rate=500000,
        bus_members=[
            LINMasterInterface(name="Master1", bus_ref="Bus1", lin_protocol="LIN2.0", p2_min=0.1, st_min=0.1),
            LINMasterInterface(name="Master2", bus_ref="Bus1", lin_protocol="LIN2.0", p2_min=0.1, st_min=0.1)
        ]
    )
except ValidationError as e:
    print("Validation failed")
    sys.exit(0)
else:
    print("SUCCESS")
    sys.exit(0)
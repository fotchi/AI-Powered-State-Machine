import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.lin_interface import LINMasterInterface

try:
    lin_master1 = LINMasterInterface(
        name="Master1",
        bus_ref="LINBus1",
        lin_protocol="LIN2.0",
        p2_min=0.1,
        st_min=0.2
    )
    lin_master2 = LINMasterInterface(
        name="Master2",
        bus_ref="LINBus1",
        lin_protocol="LIN2.0",
        p2_min=0.1,
        st_min=0.2
    )
except ValidationError as e:
    sys.exit(0)
else:
    print("SUCCESS")
    sys.exit(1)
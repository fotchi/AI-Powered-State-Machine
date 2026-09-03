import sys
from pydantic import ValidationError

from flync.model.flync_4_ecu.lin_interface import LINFrameRef
from flync.model.flync_4_ecu.lin_interface import LINMasterInterface

try:
    lin_frame_ref = LINFrameRef(
        bus_ref="demo_bus_ref",
        frame_ref=1,
    )
    lin_master_interface = LINMasterInterface(
        name="demo_name",
        bus_ref="demo_bus_ref",
        lin_protocol=None,
        p2_min=1.0,
        st_min=1.0,
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

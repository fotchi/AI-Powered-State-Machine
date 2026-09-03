import sys
from flync.model.flync_4_ecu.lin_interface import LINMasterInterface
from pydantic import ValidationError

lin_master = LINMasterInterface(
    name="LIN Master Interface",
    node_type='master',
    bus_ref="CAN Bus 1",
    lin_protocol=_LINProtocol.LIN,
    p2_min=0.5,
    st_min=10.0,
    sender_frames=[
        LINFrameRef(frame_ref=1),
        LINFrameRef(frame_ref=2)
    ]
)

print("SUCCESS")
sys.exit(0)
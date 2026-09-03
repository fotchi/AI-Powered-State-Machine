import sys
from pydantic import ValidationError

from flync.model.flync_4_signal.forwarder import CANFrameForwarder
from flync.model.flync_4_signal.forwarder import EthSocketEgress
from flync.model.flync_4_signal.frame import Frame

try:
    can_frame_forwarder = CANFrameForwarder(
        frame_ref="demo_frame_ref",
        egresses=[],
    )
    eth_socket_egress = EthSocketEgress(
        socket_ref="demo_socket_ref",
    )
    frame = Frame(
        name="demo_name",
        length=1,
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

import sys
from pydantic import ValidationError

from flync.model.flync_4_signal.frame import CANFrame
from flync.model.flync_4_signal.frame import Frame
from flync.model.flync_4_signal.pdu import StandardPDU

try:
    can_frame = CANFrame(
        name="demo_name",
        length=1,
        can_id=1,
        id_format='standard_11bit',
    )
    frame = Frame(
        name="demo_name",
        length=1,
    )
    standard_pdu = StandardPDU(
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
